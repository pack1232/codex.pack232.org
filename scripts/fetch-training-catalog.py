#!/usr/bin/env python3
"""Fetch BSA training catalog from training.scouting.org API.

Requires authentication. Pass your zanma_sid cookie value as an argument
or set the BSA_SESSION_TOKEN environment variable.

Usage:
  python3 scripts/fetch-training-catalog.py <zanma_sid_cookie_value>
  # or
  BSA_SESSION_TOKEN=<value> python3 scripts/fetch-training-catalog.py
"""

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / '_data'

BASE_URL = 'https://training.scouting.org/api/v1/content'
COURSES_OUTPUT = DATA_DIR / 'bsa-courses-raw.json'
PLANS_OUTPUT = DATA_DIR / 'bsa-learning-plans-raw.json'

PER_PAGE = 100


def get_token():
    """Get session token from CLI arg or env var."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    token = os.environ.get('BSA_SESSION_TOKEN')
    if token:
        return token
    print('Error: No session token provided.', file=sys.stderr)
    print('Usage: python3 scripts/fetch-training-catalog.py <zanma_sid_cookie>', file=sys.stderr)
    print('  or set BSA_SESSION_TOKEN env var', file=sys.stderr)
    sys.exit(1)


def fetch_page(token, content_type, page):
    """Fetch a single page of content from the API."""
    url = (
        f'{BASE_URL}?active[eq]=true'
        f'&includesContentType[]={content_type}'
        f'&per_page={PER_PAGE}&page={page}'
    )
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


def fetch_all(token, content_type):
    """Fetch all pages for a content type."""
    all_items = []
    page = 1

    while True:
        print(f'  Fetching {content_type} page {page}...')
        result = fetch_page(token, content_type, page)

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


def main():
    token = get_token()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Fetch courses
    print('Fetching courses...')
    courses, courses_total = fetch_all(token, 'Course')
    with open(COURSES_OUTPUT, 'w') as f:
        json.dump(courses, f, indent=2)
    print(f'Saved {len(courses)} courses to {COURSES_OUTPUT}')

    # Fetch learning plans
    print('\nFetching learning plans...')
    plans, plans_total = fetch_all(token, 'Plan')
    with open(PLANS_OUTPUT, 'w') as f:
        json.dump(plans, f, indent=2)
    print(f'Saved {len(plans)} learning plans to {PLANS_OUTPUT}')

    print(f'\nDone. {len(courses)} courses + {len(plans)} learning plans fetched.')


if __name__ == '__main__':
    main()
