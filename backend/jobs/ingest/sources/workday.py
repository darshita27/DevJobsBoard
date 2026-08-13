"""Workday CXS API (verified live for Adobe, NVIDIA, Salesforce).

Search returns a shallow list; the description needs a second call per posting,
so detail fetches are capped to keep a manual run bounded.
"""

import re
import time
from datetime import date, timedelta

from ..http import fetch_json
from ..roles import match_bucket, matches_location
from ..text import strip_html

MAX_DETAILS_PER_TENANT = 12
COUNTRY = 'India'

TENANTS = [
    {'host': 'adobe.wd5.myworkdayjobs.com', 'tenant': 'adobe', 'site': 'external_experienced', 'company': 'Adobe'},
    {'host': 'nvidia.wd5.myworkdayjobs.com', 'tenant': 'nvidia', 'site': 'NVIDIAExternalCareerSite', 'company': 'NVIDIA'},
    {'host': 'salesforce.wd12.myworkdayjobs.com', 'tenant': 'salesforce', 'site': 'External_Career_Site', 'company': 'Salesforce'},
]
QUERIES = ['software engineer', 'full stack', 'frontend', 'intern']


def _parse_posted_on(posted_on: str = ''):
    m = re.search(r'(\d+)\+?\s*Days?\s*Ago', posted_on or '', re.I)
    if m:
        return date.today() - timedelta(days=int(m.group(1)))
    if re.search(r'today', posted_on or '', re.I):
        return date.today()
    if re.search(r'yesterday', posted_on or '', re.I):
        return date.today() - timedelta(days=1)
    m30 = re.search(r'(\d+)\+?\s*Months?\s*Ago', posted_on or '', re.I)
    if m30:
        return date.today() - timedelta(days=int(m30.group(1)) * 30)
    return None


def _discover_country_facet(base, log, company):
    try:
        data = fetch_json(f'{base}/jobs', method='POST', json_body={'appliedFacets': {}, 'limit': 1, 'offset': 0, 'searchText': 'engineer'})
        for facet in data.get('facets', []) or []:
            for v in facet.get('values', []) or []:
                if re.fullmatch(COUNTRY, v.get('descriptor') or '', re.I):
                    log(f'workday: {company}: country facet "{facet["facetParameter"]}" -> {COUNTRY} ({v.get("count")} jobs)')
                    return {'param': facet['facetParameter'], 'id': v['id']}
        log(f'workday: {company}: no "{COUNTRY}" facet exposed; falling back to unfiltered search', warn=True)
    except Exception as err:  # noqa: BLE001
        log(f'workday: {company}: facet discovery failed ({err}); falling back to unfiltered search', warn=True)
    return None


def fetch_workday(log):
    out = []

    for t in TENANTS:
        base = f"https://{t['host']}/wday/cxs/{t['tenant']}/{t['site']}"
        seen = {}

        facet = _discover_country_facet(base, log, t['company'])
        applied_facets = {facet['param']: [facet['id']]} if facet else {}

        for q in QUERIES:
            try:
                data = fetch_json(f'{base}/jobs', method='POST', json_body={'appliedFacets': applied_facets, 'limit': 20, 'offset': 0, 'searchText': q})
                postings = data.get('jobPostings', []) or []
                for p in postings:
                    path = p.get('externalPath')
                    if path and path not in seen:
                        seen[path] = p
                log(f'workday: {t["company"]} "{q}" -> {len(postings)} raw')
            except Exception as err:  # noqa: BLE001
                log(f'workday: {t["company"]} query "{q}" failed: {err}', warn=True)
            time.sleep(0.4)

        # Prefilter on the shallow record BEFORE spending the detail-fetch budget,
        # otherwise the cap gets consumed by roles the pipeline would discard anyway.
        all_postings = list(seen.values())
        relevant = [p for p in all_postings if match_bucket(p.get('title')) and matches_location(p.get('locationsText'))]
        postings = relevant[:MAX_DETAILS_PER_TENANT]
        log(f'workday: {t["company"]}: {len(all_postings)} unique -> {len(relevant)} relevant -> fetching {len(postings)} details')

        for p in postings:
            description = ' '.join(p.get('bulletFields', []) or [])
            path = p.get('externalPath')
            try:
                detail = fetch_json(f'{base}{path}', retries=1)
                info = detail.get('jobPostingInfo', {}) or {}
                description = strip_html(info.get('jobDescription') or description)
                out.append({
                    'source': f"workday:{t['tenant']}",
                    'company': t['company'],
                    'title': info.get('title') or p.get('title'),
                    'location': info.get('location') or p.get('locationsText') or 'Not specified',
                    'apply_url': info.get('externalUrl') or f"https://{t['host']}/{t['site']}{path}",
                    'posted_date': _parse_posted_on(p.get('postedOn')),
                    'description': description,
                })
            except Exception as err:  # noqa: BLE001
                log(f'workday: {t["company"]} detail {path} failed: {err}', warn=True)
                out.append({
                    'source': f"workday:{t['tenant']}",
                    'company': t['company'],
                    'title': p.get('title'),
                    'location': p.get('locationsText') or 'Not specified',
                    'apply_url': f"https://{t['host']}/{t['site']}{path}",
                    'posted_date': _parse_posted_on(p.get('postedOn')),
                    'description': description,
                })
            time.sleep(0.45)

    return out
