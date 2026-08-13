"""Amazon Jobs public search endpoint (verified live)."""

import re
import time
from urllib.parse import urlencode

from ..http import fetch_json
from ..text import strip_html, to_iso_date

BASE = 'https://www.amazon.jobs/en/search.json'
QUERIES = ['software development engineer', 'front end engineer', 'full stack', 'software engineer intern', 'machine learning']
COUNTRY_CODES = ['IND']


def clean_amazon_entity(name: str = '') -> str:
    n = (name or '').strip()
    if not n:
        return 'Amazon'
    if re.search(r'amazon web services|^aws\b', n, re.I):
        return 'Amazon Web Services (AWS)'
    if re.search(r'^adci\b|amazon development c|amazon\.com|amazon corporate|^amazon\b', n, re.I):
        return 'Amazon'
    if re.search(r'audible', n, re.I):
        return 'Audible (Amazon)'
    if re.search(r'kuiper', n, re.I):
        return 'Project Kuiper (Amazon)'
    return n


def fetch_amazon(log):
    out = []
    combos = [(q, cc) for q in QUERIES for cc in COUNTRY_CODES]

    for q, loc in combos:
        # normalized_country_code[] is the only location param this endpoint honours.
        params = urlencode({'base_query': q, 'result_limit': '50', 'sort': 'recent'})
        params += f'&normalized_country_code[]={loc}'
        url = f'{BASE}?{params}'
        try:
            data = fetch_json(url)
            jobs = data.get('jobs', []) or []
            for j in jobs:
                description = strip_html('\n\n'.join(filter(None, [
                    j.get('description'), j.get('basic_qualifications'), j.get('preferred_qualifications'),
                ])))
                out.append({
                    'source': 'amazon',
                    'company': clean_amazon_entity(j.get('company_name')),
                    'title': j.get('title'),
                    'location': j.get('normalized_location') or j.get('location') or 'India',
                    'apply_url': f"https://www.amazon.jobs{j['job_path']}" if j.get('job_path') else 'https://www.amazon.jobs',
                    'posted_date': to_iso_date(j.get('posted_date')),
                    'description': description,
                })
            log(f'amazon: "{q}" @ {loc} -> {len(jobs)} raw')
        except Exception as err:  # noqa: BLE001
            log(f'amazon: query "{q}" @ {loc} failed: {err}', warn=True)
        time.sleep(0.7)

    return out
