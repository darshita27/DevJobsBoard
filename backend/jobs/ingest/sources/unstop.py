"""Unstop public opportunity-search API (verified live, no auth required).

Endpoint accepts a free-text `searchTerm`, an `opportunity` type ('jobs' or
'internships'), and `oppstatus=open` to only return postings still accepting
applications — that last filter alone drops the ~1500 raw hits for a broad
term like "full stack" down to a couple dozen still-open ones.
"""

import time
from urllib.parse import urlencode

from ..http import fetch_json
from ..text import strip_html, to_iso_date

BASE = 'https://unstop.com/api/public/opportunity/search-result'

JOB_QUERIES = [
    'full stack developer', 'frontend developer', 'backend developer',
    'react developer', 'node js developer', 'mern stack developer', 'web developer',
]
INTERN_QUERIES = [
    'full stack developer intern', 'software engineer intern', 'web developer intern',
    'machine learning intern', 'generative ai intern',
]

WORK_MODE_LABELS = {'remote': 'Remote', 'hybrid': 'Hybrid', 'in_office': 'On-site'}


def _location_str(item):
    cities = [loc.get('city') for loc in (item.get('locations') or []) if loc.get('city')]
    if cities:
        return f"{', '.join(dict.fromkeys(cities))}, India"
    return 'India'


def _to_posting(item, opportunity):
    job_detail = item.get('jobDetail') or {}
    location = _location_str(item)
    mode_label = WORK_MODE_LABELS.get(job_detail.get('type'))
    if mode_label:
        location = f'{location} ({mode_label})'

    return {
        'source': f'unstop:{opportunity}',
        'company': (item.get('organisation') or {}).get('name') or 'Unknown',
        'title': item.get('title'),
        'location': location,
        'apply_url': item.get('seo_url') or item.get('short_url'),
        'posted_date': to_iso_date(item.get('approved_date') or item.get('updated_at')),
        'description': strip_html(item.get('details') or ''),
    }


def _run_queries(queries, opportunity, log, seen):
    for q in queries:
        params = urlencode({
            'opportunity': opportunity, 'oppstatus': 'open', 'page': 1, 'per_page': 30, 'searchTerm': q,
        })
        try:
            data = fetch_json(f'{BASE}?{params}')
            items = ((data.get('data') or {}).get('data')) or []
            for item in items:
                if item.get('id') not in seen:
                    seen[item['id']] = _to_posting(item, opportunity)
            log(f'unstop: {opportunity} "{q}" -> {len(items)} raw')
        except Exception as err:  # noqa: BLE001
            log(f'unstop: {opportunity} query "{q}" failed: {err}', warn=True)
        time.sleep(0.5)


def fetch_unstop(log):
    seen = {}
    _run_queries(JOB_QUERIES, 'jobs', log, seen)
    _run_queries(INTERN_QUERIES, 'internships', log, seen)
    return list(seen.values())
