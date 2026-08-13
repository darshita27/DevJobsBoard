import json
import logging
import os

import anthropic
from django.conf import settings

logger = logging.getLogger(__name__)


class ResumeTailorError(Exception):
    pass


SYSTEM_PROMPT = """You are an expert resume writer and ATS (Applicant Tracking System) optimization specialist. Rewrite resumes so they pass automated ATS keyword screening and read well to a human recruiter, for the specific job the candidate is applying to.

Rules:
- Never invent employers, job titles, dates, degrees, certifications, or skills the candidate did not provide. Only reorganize, rephrase, and emphasize what is genuinely present in the original resume.
- Naturally weave in keywords and phrases from the job description wherever the candidate's real experience genuinely supports them. Do not keyword-stuff.
- Quantify achievements only where the original resume already gives you a number or a clear basis to state one plainly.
- ATS-friendly formatting only: plain text, no tables, no columns, no graphics, no special unicode bullets — use a plain hyphen "-" for bullets. Standard section headers: Summary, Skills, Experience, Education, Certifications (omit any section the candidate has no content for).
- Reverse-chronological order within Experience and Education.
- Keep the candidate's actual contact info section exactly as given if present.
- Do not pad with generic filler ("results-driven professional", "team player") unless the original resume already frames itself that way.
"""

RESPONSE_SCHEMA = {
    'type': 'object',
    'properties': {
        'tailored_resume': {
            'type': 'string',
            'description': 'The full rewritten resume as plain text, ATS-friendly formatting only.',
        },
        'summary_of_changes': {
            'type': 'array', 'items': {'type': 'string'},
            'description': '3-6 bullet points on what was changed and why.',
        },
        'matched_keywords': {
            'type': 'array', 'items': {'type': 'string'},
            'description': 'Keywords/phrases from the job description that now appear in the tailored resume.',
        },
        'ats_tips': {
            'type': 'array', 'items': {'type': 'string'},
            'description': (
                '2-4 short, actionable tips for the candidate to further improve ATS match — things '
                'that could not be fixed by rewriting alone (e.g. "add a certification in X if you have one").'
            ),
        },
    },
    'required': ['tailored_resume', 'summary_of_changes', 'matched_keywords', 'ats_tips'],
    'additionalProperties': False,
}


def extract_text_from_upload(uploaded_file) -> str:
    name = (uploaded_file.name or '').lower()
    if name.endswith('.pdf'):
        import pypdf
        reader = pypdf.PdfReader(uploaded_file)
        return '\n'.join((page.extract_text() or '') for page in reader.pages)
    if name.endswith('.docx'):
        import docx
        document = docx.Document(uploaded_file)
        return '\n'.join(p.text for p in document.paragraphs)
    if name.endswith('.txt'):
        return uploaded_file.read().decode('utf-8', errors='ignore')
    raise ValueError('Unsupported file type — upload a .pdf, .docx, or .txt resume.')


def tailor_resume(resume_text: str, job_description: str, job_title: str = '', company: str = '') -> dict:
    if not os.environ.get('ANTHROPIC_API_KEY'):
        raise ResumeTailorError(
            'Resume tailoring is not configured yet — ANTHROPIC_API_KEY is missing from the server environment.'
        )

    client = anthropic.Anthropic()
    user_content = (
        f'JOB TITLE: {job_title or "Not specified"}\n'
        f'COMPANY: {company or "Not specified"}\n\n'
        f'JOB DESCRIPTION:\n{job_description}\n\n'
        '---\n\n'
        f"CANDIDATE'S CURRENT RESUME:\n{resume_text}"
    )
    try:
        response = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            output_config={'format': {'type': 'json_schema', 'schema': RESPONSE_SCHEMA}},
            messages=[{'role': 'user', 'content': user_content}],
        )
    except anthropic.AuthenticationError as err:
        logger.exception('Anthropic auth failed')
        raise ResumeTailorError('Resume tailoring is not configured (invalid API key).') from err
    except anthropic.RateLimitError as err:
        raise ResumeTailorError('Rate limited by the AI provider — try again shortly.') from err
    except anthropic.APIStatusError as err:
        logger.exception('Anthropic API error')
        raise ResumeTailorError('The AI provider returned an error while tailoring your resume.') from err
    except anthropic.APIConnectionError as err:
        raise ResumeTailorError('Could not reach the AI provider — check your connection and try again.') from err
    except Exception as err:  # noqa: BLE001 - never let an SDK-internal error surface as a raw 500
        logger.exception('Unexpected error calling Anthropic')
        raise ResumeTailorError('Resume tailoring is not configured correctly on the server.') from err

    text_block = next((b.text for b in response.content if b.type == 'text'), None)
    if not text_block:
        raise ResumeTailorError('The AI provider did not return usable output.')
    try:
        return json.loads(text_block)
    except json.JSONDecodeError as err:
        raise ResumeTailorError('The AI provider returned malformed output.') from err
