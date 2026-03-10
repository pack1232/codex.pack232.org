#!/usr/bin/env python3
"""Generate training directory structure from BSA course data.

Reads raw JSON from _data/bsa-courses-raw.json and _data/bsa-learning-plans-raw.json,
then generates:
  - training/README.md (nav parent)
  - training/courses/README.md (category listing)
  - training/courses/{course-code}.md (one per course)
  - training/learning-plans/README.md (category listing)
  - training/learning-plans/{plan-code}.md (one per plan)
  - roles/*/training.yaml (role training requirements)

Usage: python3 scripts/generate-training.py
"""

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / '_data'
TRAINING_DIR = REPO_ROOT / 'training'
COURSES_DIR = TRAINING_DIR / 'courses'
PLANS_DIR = TRAINING_DIR / 'learning-plans'
ROLES_DIR = REPO_ROOT / 'roles'

COURSES_RAW = DATA_DIR / 'bsa-courses-raw.json'
PLANS_RAW = DATA_DIR / 'bsa-learning-plans-raw.json'


def slugify(code):
    """Convert a course code like SCO_471 to sco-471."""
    return code.lower().replace('_', '-')


def extract_course_code(item):
    """Extract the course code (contentId) from a raw API item."""
    return item.get('contentId', '')


def extract_fields(item):
    """Extract the fields we care about from a raw API item."""
    code = extract_course_code(item)
    return {
        'code': code,
        'slug': slugify(code),
        'name': item.get('name', '').strip(),
        'description': (item.get('description') or '').strip(),
        'duration': item.get('duration'),  # minutes
        'type': item.get('type', ''),
        'url': item.get('url', f'https://training.scouting.org/courses/{code}'),
    }


def escape_yaml_string(s):
    """Escape a string for YAML double-quoted value."""
    if not s:
        return ''
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')


def write_course_md(filepath, course, category, parent):
    """Write a single course/plan markdown file."""
    desc_escaped = escape_yaml_string(course['description'])
    # Truncate description for frontmatter if very long
    fm_desc = desc_escaped[:300] if len(desc_escaped) > 300 else desc_escaped
    duration = course['duration'] if course['duration'] else 0

    with open(filepath, 'w') as f:
        f.write('---\n')
        f.write(f'title: "{escape_yaml_string(course["name"])}"\n')
        f.write(f'course_id: {course["slug"]}\n')
        f.write(f'course_code: "{course["code"]}"\n')
        f.write(f'category: {category}\n')
        f.write(f'duration: {duration}\n')
        f.write(f'description: "{fm_desc}"\n')
        f.write(f'url: "{course["url"]}"\n')
        f.write(f'parent: "{parent}"\n')
        f.write('nav_exclude: true\n')
        f.write('---\n\n')
        f.write(f'# {course["name"]}\n\n')
        if course['description']:
            f.write(f'{course["description"]}\n\n')
        f.write('## Details\n\n')
        f.write(f'- **Course Code**: {course["code"]}\n')
        f.write(f'- **Duration**: {duration} minutes\n')
        f.write(f'- **URL**: [Take this course]({course["url"]})\n')


def generate_training_yamls():
    """Generate training.yaml for each role based on BSA requirements."""
    # Course code mapping from the trained-leader-requirements doc
    # These are the Cub Scout position-specific codes only
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

    # Role -> training courses mapping
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
    # Load raw data
    if not COURSES_RAW.exists():
        print(f'Error: {COURSES_RAW} not found. Run fetch-training-catalog.py first.', file=sys.stderr)
        sys.exit(1)

    with open(COURSES_RAW) as f:
        raw_courses = json.load(f)

    plans_data = []
    if PLANS_RAW.exists():
        with open(PLANS_RAW) as f:
            plans_data = json.load(f)

    # Create directories
    COURSES_DIR.mkdir(parents=True, exist_ok=True)
    PLANS_DIR.mkdir(parents=True, exist_ok=True)

    # Write training/README.md (nav parent)
    with open(TRAINING_DIR / 'README.md', 'w') as f:
        f.write('---\n')
        f.write('title: Training\n')
        f.write('nav_order: 5\n')
        f.write('has_children: true\n')
        f.write('nav_exclude: false\n')
        f.write('permalink: /training/\n')
        f.write('---\n\n')
        f.write('# Training\n\n')
        f.write('Scouting America training courses and learning plans for Pack 232 leaders.\n\n')
        f.write('- [Courses](/training/courses/) — Individual training modules\n')
        f.write('- [Learning Plans](/training/learning-plans/) — Curated course sequences\n')

    # Write training/courses/README.md
    with open(COURSES_DIR / 'README.md', 'w') as f:
        f.write('---\n')
        f.write('title: Courses\n')
        f.write('parent: Training\n')
        f.write('has_children: false\n')
        f.write('nav_exclude: false\n')
        f.write('nav_order: 1\n')
        f.write('---\n\n')
        f.write('# Courses\n\n')
        f.write('All Scouting America training courses available through [training.scouting.org](https://training.scouting.org).\n\n')
        f.write('{% include category-training.html category="courses" %}\n')

    # Write training/learning-plans/README.md
    with open(PLANS_DIR / 'README.md', 'w') as f:
        f.write('---\n')
        f.write('title: Learning Plans\n')
        f.write('parent: Training\n')
        f.write('has_children: false\n')
        f.write('nav_exclude: false\n')
        f.write('nav_order: 2\n')
        f.write('---\n\n')
        f.write('# Learning Plans\n\n')
        f.write('Curated course sequences for specific roles and topics from [training.scouting.org](https://training.scouting.org).\n\n')
        f.write('{% include category-training.html category="learning-plans" %}\n')

    # Generate course files
    course_count = 0
    seen_slugs = set()
    for item in raw_courses:
        course = extract_fields(item)
        if not course['code'] or not course['name']:
            continue
        slug = course['slug']
        # Handle duplicates
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        filepath = COURSES_DIR / f'{slug}.md'
        write_course_md(filepath, course, 'courses', 'Courses')
        course_count += 1

    print(f'Generated {course_count} course files in {COURSES_DIR}')

    # Generate learning plan files
    plan_count = 0
    seen_plan_slugs = set()
    for item in plans_data:
        plan = extract_fields(item)
        if not plan['code'] or not plan['name']:
            continue
        slug = plan['slug']
        if slug in seen_plan_slugs:
            continue
        seen_plan_slugs.add(slug)

        filepath = PLANS_DIR / f'{slug}.md'
        write_course_md(filepath, plan, 'learning-plans', 'Learning Plans')
        plan_count += 1

    print(f'Generated {plan_count} learning plan files in {PLANS_DIR}')

    # Generate training.yaml for each role
    role_count = generate_training_yamls()
    print(f'Generated training.yaml for {role_count} roles')

    print(f'\nDone. {course_count} courses + {plan_count} plans + {role_count} role training files.')


if __name__ == '__main__':
    main()
