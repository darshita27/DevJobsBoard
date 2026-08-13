"""Text-processing helpers ported from the dev-jobs-blog scraper's src/lib/text.js.

Kept deliberately self-contained (no import of the other project) so this app
has no runtime dependency on a sibling repo.
"""

import hashlib
import re
from datetime import datetime, timezone

from dateutil import parser as dateutil_parser

CITY_ALIASES = {
    'bengaluru': 'bangalore', 'blr': 'bangalore',
    'gurugram': 'gurgaon', 'new delhi': 'delhi', 'ncr': 'delhi',
    'bombay': 'mumbai', 'madras': 'chennai', 'calcutta': 'kolkata',
    'trivandrum': 'thiruvananthapuram', 'vizag': 'visakhapatnam',
}

SKILL_VOCAB = [
    'JavaScript', 'TypeScript', 'Python', 'Java', 'Go', 'Golang', 'Rust', 'C++', 'C#', 'Kotlin', 'Swift', 'PHP', 'Ruby', 'Scala',
    'React', 'React Native', 'Next.js', 'Angular', 'Vue', 'Svelte', 'Redux', 'jQuery',
    'Node.js', 'Express', 'NestJS', 'Django', 'Flask', 'FastAPI', 'Spring Boot', 'Spring', 'Rails', 'Laravel', '.NET',
    'HTML', 'CSS', 'SASS', 'Tailwind', 'Bootstrap', 'Webpack', 'Vite',
    'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch', 'DynamoDB', 'Cassandra', 'SQL', 'NoSQL', 'Prisma',
    'GraphQL', 'REST', 'gRPC', 'WebSocket', 'Microservices',
    'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins', 'CI/CD', 'Git', 'Linux',
    'TensorFlow', 'PyTorch', 'Keras', 'scikit-learn', 'Pandas', 'NumPy', 'OpenCV', 'Hugging Face',
    'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'LLM', 'RAG', 'LangChain', 'Generative AI',
    'Prompt Engineering', 'Transformers', 'Fine-tuning', 'Vector Database', 'Embeddings',
    'Agile', 'Scrum', 'Jest', 'Cypress', 'Selenium', 'JUnit',
]


def strip_html(html: str = '') -> str:
    html = html or ''
    html = re.sub(r'<(script|style)[^>]*>[\s\S]*?</\1>', ' ', html, flags=re.I)
    html = re.sub(r'<li[^>]*>', '\n- ', html, flags=re.I)
    html = re.sub(r'</(p|div|br|h\d|ul|ol)>', '\n', html, flags=re.I)
    html = re.sub(r'<[^>]+>', ' ', html)
    html = (
        html.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<')
        .replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    )
    html = re.sub(r'&[a-z]+;', ' ', html, flags=re.I)
    html = re.sub(r'[ \t]+', ' ', html)
    html = re.sub(r'\n{3,}', '\n\n', html)
    return html.strip()


def norm_company(s: str = '') -> str:
    s = (s or '').lower()
    s = re.sub(
        r'\b(private|pvt|limited|ltd|llp|inc|incorporated|corp|corporation|technologies|technology|labs|india|software|services|solutions|systems|global)\b',
        '', s,
    )
    return re.sub(r'[^a-z0-9]', '', s).strip()


def norm_title(s: str = '') -> str:
    s = (s or '').lower()
    s = re.sub(r'\((.*?)\)', ' ', s)
    s = re.sub(
        r'\b(i{1,3}|iv|v|sr|senior|jr|junior|\d{4}|20\d\d|batch|hiring|urgent|immediate|remote|wfh|full[\s-]?time|part[\s-]?time)\b',
        ' ', s,
    )
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return re.sub(r'\s+', ' ', s.strip())


def norm_city(s: str = '') -> str:
    raw = (s or '').lower()
    c = re.split(r'[,|/•]', raw)[0]
    c = re.sub(r'\b(india|karnataka|maharashtra|telangana|tamil nadu|haryana|uttar pradesh|west bengal|kerala)\b', '', c)
    c = re.sub(r'[^a-z\s]', '', c).strip()
    c = re.sub(r'\s+', ' ', c)
    if re.search(r'remote|anywhere|work from home|wfh', raw):
        c = 'remote'
    return CITY_ALIASES.get(c, c)


def fingerprint(company: str, title: str, location: str) -> str:
    key = f'{norm_company(company)}|{norm_title(title)}|{norm_city(location)}'
    return hashlib.sha1(key.encode('utf-8')).hexdigest()[:16]


def detect_work_mode(*blobs) -> str:
    t = ' '.join(b for b in blobs if b).lower()
    if re.search(r'\bhybrid\b', t):
        return 'hybrid'
    if re.search(r'\b(fully remote|remote|work from home|wfh|telecommute)\b', t):
        return 'remote'
    if re.search(r'\b(on[-\s]?site|in[-\s]?office|onsite|in person)\b', t):
        return 'onsite'
    return 'unspecified'


def extract_skills(text: str = '', limit: int = 12) -> list[str]:
    hay = f' {text.lower()} '
    found = []
    for skill in SKILL_VOCAB:
        s = skill.lower()
        esc = re.escape(s)
        boundary = rf'(?<![a-z0-9]){esc}(?![a-z0-9])' if re.match(r'^[a-z0-9]', s) else esc
        if re.search(boundary, hay) and skill not in found:
            found.append(skill)
        if len(found) >= limit:
            break
    return found


def is_intern_title(title: str = '') -> bool:
    return bool(re.search(r'\b(intern|internship|trainee|co[-\s]?op|apprentice|summer analyst)\b', title or '', re.I))


def extract_experience(text: str = '', title: str = ''):
    """Returns (display_text, min_years, max_years) — max_years=None means 'and above'."""
    if is_intern_title(title):
        m = re.search(r'(\d+)\s*(?:-|–|to)\s*(\d+)\s*(?:month|week)s?', text, re.I)
        if m:
            return f'Internship ({m.group(0).strip()})', 0, 1
        return 'Internship — no prior professional experience required', 0, 1

    body = re.sub(r'non[-\s]?internship', ' ', text, flags=re.I)

    range_m = re.search(r'(\d{1,2})\s*(?:\+|to|-|–)\s*(\d{1,2})?\s*\+?\s*(?:years?|yrs?)', body, re.I)
    if range_m:
        lo = int(range_m.group(1))
        hi = range_m.group(2)
        if hi and int(hi) > lo:
            return f'{lo}–{int(hi)} years', lo, int(hi)
        return f'{lo}+ years', lo, None

    single_m = re.search(r'(\d{1,2})\s*(?:years?|yrs?)\s+(?:of\s+)?(?:relevant\s+|professional\s+)?experience', body, re.I)
    if single_m:
        lo = int(single_m.group(1))
        return f'{lo}+ years', lo, None

    if re.search(r'\b(fresher|entry[-\s]level|new grad|recent graduate|0\s*(?:-|–)\s*1\s*year)\b', body, re.I):
        return 'Fresher / entry level', 0, 1

    return 'Not specified', None, None


def extract_eligibility(text: str = '') -> str:
    t = text.lower()
    bits = []
    if re.search(r"\b(b\.?tech|b\.?e\.?|bachelor'?s?|undergraduate|b\.?sc|bca)\b", t):
        bits.append("Bachelor's degree (B.Tech/B.E./BCA/B.Sc) completed or in progress")
    if re.search(r"\b(m\.?tech|master'?s?|m\.?sc|mca|postgraduate)\b", t):
        bits.append("Master's degree (M.Tech/MCA/M.Sc) an advantage")
    if re.search(r'\bph\.?d\b', t):
        bits.append('PhD preferred for research-track roles')
    if re.search(r'\bcgpa\b|\b\d\.\d\s*cgpa\b|\b60%|\b70%', t):
        bits.append('Minimum academic percentage/CGPA criteria may apply')
    if not bits:
        return "Open to candidates meeting the role's technical requirements — check the official posting for degree criteria."
    return '. '.join(bits) + '.'


def extract_deadline(text: str = ''):
    patterns = [
        r'(?:apply\s+(?:by|before)|last\s+date(?:\s+to\s+apply)?|application\s+deadline|closes?\s+on)\s*[:\-–]?\s*([A-Z][a-z]{2,8}\s+\d{1,2},?\s*\d{4})',
        r'(?:apply\s+(?:by|before)|last\s+date(?:\s+to\s+apply)?|application\s+deadline|closes?\s+on)\s*[:\-–]?\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            try:
                return dateutil_parser.parse(m.group(1), fuzzy=True).date()
            except (ValueError, OverflowError):
                return None
    return None


def extract_salary(text: str = ''):
    patterns = [
        r'(?:₹|rs\.?|inr)\s?[\d,]+(?:\.\d+)?\s*(?:-|–|to)\s*(?:₹|rs\.?|inr)?\s?[\d,]+(?:\.\d+)?\s*(?:lpa|per month|/month|per annum|pa)?',
        r'(?:₹|rs\.?|inr)\s?[\d,]+(?:\.\d+)?\s*(?:lpa|per month|/month|per annum|pa)',
        r'\$\s?[\d,]+\s*(?:-|–|to)\s*\$?\s?[\d,]+\s*(?:per hour|/hr|per year|/yr)?',
        r'\b\d{1,3}\s*(?:-|–|to)\s*\d{1,3}\s*lpa\b',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            return re.sub(r'\s+', ' ', m.group(0)).strip()
    return None


def to_iso_date(value):
    if not value:
        return None
    try:
        return dateutil_parser.parse(str(value), fuzzy=True).date()
    except (ValueError, OverflowError):
        return None


def days_ago(date_value):
    if not date_value:
        return None
    d = date_value if hasattr(date_value, 'year') else to_iso_date(date_value)
    if not d:
        return None
    today = datetime.now(timezone.utc).date()
    return (today - d).days
