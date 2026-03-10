#!/usr/bin/env python3
"""Fetch BSA training catalog from training.scouting.org API.

Fetches all active training content (courses, learning plans, programs) in a
single unfiltered request and saves to _data/bsa-training-catalog-raw.json.

Requires authentication. Pass your zanma_sid cookie value as an argument
or set the BSA_SESSION_TOKEN environment variable.

Usage:
  python3 .claude/skills/bsa-training-fetch/scripts/fetch-training-catalog.py <zanma_sid_cookie_value>
  # or
  BSA_SESSION_TOKEN=<value> python3 .claude/skills/bsa-training-fetch/scripts/fetch-training-catalog.py
"""

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DATA_DIR = REPO_ROOT / '_data'

BASE_URL = 'https://training.scouting.org/api/v1/content'
CATALOG_OUTPUT = DATA_DIR / 'bsa-training-catalog-raw.json'

PER_PAGE = 100


def get_token():
    """Get session token from CLI arg or env var."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    token = os.environ.get('BSA_SESSION_TOKEN')
    if token:
        return token
    print('Error: No session token provided.', file=sys.stderr)
    print('Usage: python3 .claude/skills/bsa-training-fetch/scripts/fetch-training-catalog.py <zanma_sid_cookie>', file=sys.stderr)
    print('  or set BSA_SESSION_TOKEN env var', file=sys.stderr)
    sys.exit(1)


def fetch_page(token, page):
    """Fetch a single page of all active content from the API."""
    url = f'{BASE_URL}?active[eq]=true&per_page={PER_PAGE}&page={page}'
    req = Request(url)
    req.add_header('Accept', 'application/json')
    req.add_header('Cookie', f'zanma_sid={token}')

    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        if e.code == 401:
            print('Error: Authentication failed (401). Your session token may have expired.', file=sys.stderr)
            print('Log in again at training.scouting.org and copy a fresh zanma_sid cookie.', file=sys.stderr)
            sys.exit(1)
        raise


def fetch_all(token):
    """Fetch all pages of active training content."""
    all_items = []
    page = 1

    while True:
        print(f'  Fetching page {page}...')
        result = fetch_page(token, page)

        items = result.get('data', [])
        # Strip user-specific progress data
        for item in items:
            item.pop('progresses', None)

        all_items.extend(items)

        pagination = result.get('_pagination', {})
        total = pagination.get('total_records', 0)
        links = pagination.get('_links', {})

        print(f'    Got {len(items)} items (total so far: {len(all_items)}/{total})')

        if links.get('next') is None or len(all_items) >= total:
            break

        page += 1

    return all_items, total


# Map API type field to our directory names
TYPE_MAP = {
    'Course': 'courses',
    'Plan': 'learning-plans',
    'Program': 'programs',
}


def classify_items(items):
    """Count items by type using the API type field."""
    counts = {}
    for item in items:
        api_type = item.get('type', 'unknown')
        item_type = TYPE_MAP.get(api_type, api_type.lower())
        counts[item_type] = counts.get(item_type, 0) + 1
    return counts


def main():
    token = get_token()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print('Fetching all training content...')
    items, total = fetch_all(token)

    with open(CATALOG_OUTPUT, 'w') as f:
        json.dump(items, f, indent=2)

    counts = classify_items(items)
    print(f'\nSaved {len(items)} items to {CATALOG_OUTPUT}')
    print('Breakdown by type:')
    for item_type, count in sorted(counts.items()):
        print(f'  {item_type}: {count}')

    print(f'\nDone. {len(items)} total training items fetched.')


if __name__ == '__main__':
    main()
