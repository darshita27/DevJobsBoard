"""Greenhouse public Job Board API (verified live for Razorpay, PhonePe, Groww, Postman)."""

import time

from ..http import fetch_json
from ..text import strip_html, to_iso_date

BOARDS = [
    {'slug': 'razorpaysoftwareprivatelimited', 'company': 'Razorpay'},
    {'slug': 'phonepe', 'company': 'PhonePe'},
    {'slug': 'groww', 'company': 'Groww'},
    {'slug': 'postman', 'company': 'Postman'},
]


def fetch_greenhouse(log):
    out = []
    for board in BOARDS:
        url = f"https://boards-api.greenhouse.io/v1/boards/{board['slug']}/jobs?content=true"
        try:
            data = fetch_json(url)
            jobs = data.get('jobs', []) or []
            for j in jobs:
                out.append({
                    'source': f"greenhouse:{board['slug']}",
                    'company': board['company'],
                    'title': j.get('title'),
                    'location': (j.get('location') or {}).get('name') or 'Not specified',
                    'apply_url': j.get('absolute_url'),
                    'posted_date': to_iso_date(j.get('first_published') or j.get('updated_at')),
                    'description': strip_html(j.get('content') or ''),
                })
            log(f"greenhouse: {board['company']} -> {len(jobs)} raw")
        except Exception as err:  # noqa: BLE001
            log(f"greenhouse: {board['company']} ({board['slug']}) failed: {err}", warn=True)
        time.sleep(0.5)
    return out
