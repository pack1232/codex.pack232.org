#!/usr/bin/env python3
"""Generate training directory structure from BSA catalog data.

Reads _data/bsa-training-catalog-raw.json (all content types) and generates:
  - training/README.md (nav parent)
  - training/courses/README.md + training/courses/{slug}.md
  - training/learning-plans/README.md + training/learning-plans/{slug}.md
  - training/programs/README.md + training/programs/{slug}.md
  - roles/*/training.yaml (role training requirements)

The type of each item (courses, learning-plans, programs) is derived from
the first path segment of its URL on training.scouting.org.

Usage: python3 .claude/skills/bsa-training-generate/scripts/generate-training.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DATA_DIR = REPO_ROOT / '_data'
TRAINING_DIR = REPO_ROOT / 'training'
ROLES_DIR = REPO_ROOT / 'roles'

CATALOG_RAW = DATA_DIR / 'bsa-training-catalog-raw.json'

# Map API type field to our directory names
TYPE_MAP = {
    'Course': 'courses',
    'Plan': 'learning-plans',
    'Program': 'programs',
}

VALID_TYPES = set(TYPE_MAP.values())

# Display names and nav order for each type
TYPE_META = {
    'courses': {'title': 'Courses', 'nav_order': 1,
                'desc': 'All Scouting America training courses available through [training.scouting.org](https://training.scouting.org).'},
    'learning-plans': {'title': 'Learning Plans', 'nav_order': 2,
                       'desc': 'Curated course sequences for specific roles and topics from [training.scouting.org](https://training.scouting.org).'},
    'programs': {'title': 'Programs', 'nav_order': 3,
                 'desc': 'Scouting America training programs available through [training.scouting.org](https://training.scouting.org).'},
}

# Map API URL prefixes to full training.scouting.org paths
URL_PREFIX_MAP = {
    'courses': 'courses',
    'plans': 'learning-plans',
    'containers': 'programs',
}


def slugify(code):
    """Convert a course code like SCO_471 to sco-471."""
    return code.lower().replace('_', '-')


def get_item_type(item):
    """Derive the training type from the API type field."""
    api_type = item.get('type', '')
    return TYPE_MAP.get(api_type, 'courses')


def build_full_url(item):
    """Build full training.scouting.org URL from relative API url."""
    url = item.get('url', '')
    if url.startswith('http'):
        return url
    return f'https://training.scouting.org/{url}'


def extract_fields(item):
    """Extract the fields we care about from a raw API item."""
    code = item.get('contentId', '')
    item_type = get_item_type(item)
    return {
        'code': code,
        'slug': slugify(code),
        'name': item.get('name', '').strip(),
        'description': (item.get('description') or '').strip(),
        'duration': item.get('duration'),  # minutes
        'type': item_type,
        'url': build_full_url(item),
    }


def escape_yaml_string(s):
    """Escape a string for YAML double-quoted value."""
    if not s:
        return ''
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')


def write_item_md(filepath, item, parent):
    """Write a single training item markdown file."""
    desc_escaped = escape_yaml_string(item['description'])
    fm_desc = desc_escaped[:300] if len(desc_escaped) > 300 else desc_escaped
    duration = item['duration'] if item['duration'] else 0

    with open(filepath, 'w') as f:
        f.write('---\n')
        f.write(f'title: "{escape_yaml_string(item["name"])}"\n')
        f.write(f'training_id: {item["slug"]}\n')
        f.write(f'training_code: "{item["code"]}"\n')
        f.write(f'type: {item["type"]}\n')
        f.write(f'duration: {duration}\n')
        f.write(f'description: "{fm_desc}"\n')
        f.write(f'url: "{item["url"]}"\n')
        f.write(f'parent: "{parent}"\n')
        f.write('nav_exclude: true\n')
        f.write('---\n\n')
        f.write(f'# {item["name"]}\n\n')
        if item['description']:
            f.write(f'{item["description"]}\n\n')
        f.write('## Details\n\n')
        f.write(f'- **Code**: {item["code"]}\n')
        f.write(f'- **Type**: {item["type"]}\n')
        f.write(f'- **Duration**: {duration} minutes\n')
        f.write(f'- **URL**: [Take this training]({item["url"]})\n')


def write_type_readme(type_dir, item_type):
    """Write the README.md for a training type subdirectory."""
    meta = TYPE_META[item_type]
    with open(type_dir / 'README.md', 'w') as f:
        f.write('---\n')
        f.write(f'title: {meta["title"]}\n')
        f.write('parent: Training\n')
        f.write('has_children: false\n')
        f.write('nav_exclude: false\n')
        f.write(f'nav_order: {meta["nav_order"]}\n')
        f.write('---\n\n')
        f.write(f'# {meta["title"]}\n\n')
        f.write(f'{meta["desc"]}\n\n')
        f.write('{{% include category-training.html category="{}" %}}\n'.format(item_type))


def write_training_readme():
    """Write training/README.md (nav parent)."""
    with open(TRAINING_DIR / 'README.md', 'w') as f:
        f.write('---\n')
        f.write('title: Training\n')
        f.write('nav_order: 5\n')
        f.write('has_children: true\n')
        f.write('nav_exclude: false\n')
        f.write('permalink: /training/\n')
        f.write('---\n\n')
        f.write('# Training\n\n')
        f.write('Scouting America training courses, learning plans, and programs for Pack 232 leaders.\n\n')
        f.write('- [Courses](/training/courses/) — Individual training modules\n')
        f.write('- [Learning Plans](/training/learning-plans/) — Curated course sequences\n')
        f.write('- [Programs](/training/programs/) — Training programs\n')


def generate_training_yamls():
    """Generate training.yaml for each role based on BSA requirements."""
    ypt = 'y01'  # Youth Protection Training

    cubmaster_courses = [
        ('y01', 'required'),
        ('sco-450', 'required'),
        ('sco-451', 'required'),
        ('sco-453', 'required'),
        ('sco-454', 'required'),
        ('sco-457', 'required'),
        ('sco-458', 'required'),
        ('sco-462', 'required'),
    ]

    den_leader_courses = [
        ('y01', 'required'),
        ('sco-450', 'required'),
        ('sco-451', 'required'),
        ('sco-452', 'required'),
        ('sco-453', 'required'),
        ('sco-454', 'required'),
        ('sco-455', 'required'),
        ('sco-456', 'required'),
        ('sco-457', 'required'),
    ]

    pack_committee_member_courses = [
        ('y01', 'required'),
        ('sco-450', 'required'),
        ('sco-451', 'required'),
        ('sco-454', 'required'),
        ('sco-459', 'required'),
        ('sco-462', 'required'),
        ('sco-463', 'required'),
    ]

    pack_committee_chair_courses = [
        ('y01', 'required'),
        ('sco-450', 'required'),
        ('sco-451', 'required'),
        ('sco-454', 'required'),
        ('sco-459', 'required'),
        ('sco-462', 'required'),
        ('sco-463', 'required'),
    ]

    charter_org_rep_courses = [
        ('y01', 'required'),
        ('sco-450', 'required'),
        ('sco-451', 'required'),
        ('sco-454', 'required'),
        ('sco-459', 'required'),
        ('sco-462', 'required'),
        ('sco-463', 'required'),
    ]

    den_chief_courses = [
        ('y01', 'required'),
    ]

    role_training = {
        'cubmaster': cubmaster_courses,
        'assistant-cubmaster': cubmaster_courses,
        'den-leader': den_leader_courses,
        'committee-chair': pack_committee_chair_courses,
        'charter-org-rep': charter_org_rep_courses,
        'treasurer': pack_committee_member_courses,
        'secretary': pack_committee_member_courses,
        'advancement-chair': pack_committee_member_courses,
        'program-chair': pack_committee_member_courses,
        'membership-chair': pack_committee_member_courses,
        'fundraising-chair': pack_committee_member_courses,
        'den-chief': den_chief_courses,
        'popcorn-coordinator': pack_committee_member_courses,
    }

    count = 0
    for role_id, courses in role_training.items():
        role_dir = ROLES_DIR / role_id
        if not role_dir.exists():
            print(f'  Skipping {role_id} — role directory does not exist')
            continue

        filepath = role_dir / 'training.yaml'
        with open(filepath, 'w') as f:
            f.write('# Training courses for this role.\n')
            f.write(f'# Course definitions live in training/courses/{{course-id}}.md\n')
            f.write('# status: required | recommended\n\n')
            f.write('training:\n')
            for course_id, status in courses:
                f.write(f'\n  - id: {course_id}\n')
                f.write(f'    status: {status}\n')
        count += 1

    return count


def main():
    if not CATALOG_RAW.exists():
        print(f'Error: {CATALOG_RAW} not found. Run bsa-training-fetch first.', file=sys.stderr)
        sys.exit(1)

    with open(CATALOG_RAW) as f:
        raw_items = json.load(f)

    # Create directories for all types
    for item_type in VALID_TYPES:
        (TRAINING_DIR / item_type).mkdir(parents=True, exist_ok=True)

    # Write README files
    write_training_readme()
    for item_type in VALID_TYPES:
        write_type_readme(TRAINING_DIR / item_type, item_type)

    # Generate item files, grouped by type
    counts = {}
    seen_slugs = set()
    for raw_item in raw_items:
        item = extract_fields(raw_item)
        if not item['code'] or not item['name']:
            continue
        slug = item['slug']
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        item_type = item['type']
        type_dir = TRAINING_DIR / item_type
        parent = TYPE_META[item_type]['title']

        filepath = type_dir / f'{slug}.md'
        write_item_md(filepath, item, parent)
        counts[item_type] = counts.get(item_type, 0) + 1

    for item_type in sorted(counts):
        print(f'Generated {counts[item_type]} {item_type} files in {TRAINING_DIR / item_type}')

    # Generate training.yaml for each role
    role_count = generate_training_yamls()
    print(f'Generated training.yaml for {role_count} roles')

    total = sum(counts.values())
    print(f'\nDone. {total} training items ({", ".join(f"{c} {t}" for t, c in sorted(counts.items()))}) + {role_count} role training files.')


if __name__ == '__main__':
    main()
