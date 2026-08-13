import time

import requests

DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; DevJobsBoardBot/1.0)'}


def fetch_json(url, method='GET', json_body=None, retries=2, timeout=15):
    """GET/POST a URL and parse JSON, retrying transient failures a couple of times."""
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = requests.request(method, url, json=json_body, headers=DEFAULT_HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as err:  # noqa: BLE001 - genuinely want to retry on anything transient
            last_err = err
            if attempt < retries:
                time.sleep(0.5)
    raise last_err
