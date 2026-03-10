#!/usr/bin/env python3
"""Aggregate task definitions, role assignments, and training data.

Reads task definitions from tasks/**/*.md front matter and role assignments
from roles/*/tasks.yaml (simplified format), merges them, and outputs
_data/pack-tasks-generated.yaml.

Also parses events/**/*.md front matter and generates
_data/pack-events-generated.yaml with event metadata and associated tasks.

Reads training definitions from training/**/*.md front matter and role
training assignments from roles/*/training.yaml, merges them, and outputs
_data/pack-training-generated.yaml.

Usage: python3 scripts/aggregate-tasks.py
"""

import os
import re
import sys
from collections import OrderedDict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROLES_DIR = REPO_ROOT / 'roles'
TASKS_DIR = REPO_ROOT / 'tasks'
EVENTS_DIR = REPO_ROOT / 'events'
TRAINING_DIR = REPO_ROOT / 'training'
OUTPUT = REPO_ROOT / '_data' / 'pack-tasks-generated.yaml'
EVENTS_OUTPUT = REPO_ROOT / '_data' / 'pack-events-generated.yaml'
TRAINING_OUTPUT = REPO_ROOT / '_data' / 'pack-training-generated.yaml'


def get_role_id(role_dir):
    """Read role_id from README.md front matter."""
    readme = role_dir / 'README.md'
    if not readme.exists():
        return role_dir.name
    with open(readme) as f:
        content = f.read()
    if not content.startswith('---'):
        return role_dir.name
    # Extract role_id from front matter
    fm_end = content.index('---', 3)
    fm_text = content[3:fm_end]
    match = re.search(r'^role_id:\s*(.+)$', fm_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return role_dir.name


def parse_yaml_simple(filepath):
    """Parse a simple tasks.yaml without PyYAML dependency."""
    try:
        import yaml
        with open(filepath) as f:
            return yaml.safe_load(f)
    except ImportError:
        pass
    # Minimal fallback - try PyYAML via subprocess
    import subprocess, json
    result = subprocess.run(
        [sys.executable, '-c',
         f'import yaml, json; data = yaml.safe_load(open("{filepath}")); print(json.dumps(data))'],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None


def parse_front_matter(filepath):
    """Extract YAML front matter from a .md file.

    Returns a dict with front matter keys, or None if no valid front matter.
    """
    with open(filepath) as f:
        content = f.read()
    if not content.startswith('---'):
        return None
    try:
        fm_end = content.index('---', 3)
    except ValueError:
        return None
    fm_text = content[3:fm_end]

    # Try PyYAML first for robust parsing
    try:
        import yaml
        data = yaml.safe_load(fm_text)
        if isinstance(data, dict):
            return data
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: parse via subprocess
    import subprocess, json, tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
        tmp.write(fm_text)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, '-c',
             f'import yaml, json; data = yaml.safe_load(open("{tmp_path}")); print(json.dumps(data))'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    finally:
        os.unlink(tmp_path)
    return None


def main():
    warnings = []

    # ── Step 1: Read task definitions from tasks/**/*.md ──
    tasks_by_id = OrderedDict()
    if TASKS_DIR.exists():
        for tf in sorted(TASKS_DIR.glob('**/*.md')):
            if tf.name == 'README.md':
                continue
            data = parse_front_matter(str(tf))
            if not data or 'task_id' not in data:
                continue
            tid = data['task_id']
            # Extract description from body (after front matter)
            with open(tf) as f:
                content = f.read()
            fm_end = content.index('---', 3) + 3
            body = content[fm_end:].strip()
            # Get description: text between first heading and ## Schedule
            desc = ''
            lines = body.split('\n')
            in_desc = False
            desc_lines = []
            for line in lines:
                if line.startswith('# ') and not in_desc:
                    in_desc = True
                    continue
                if line.startswith('## '):
                    break
                if in_desc:
                    desc_lines.append(line)
            desc = '\n'.join(desc_lines).strip()

            tasks_by_id[tid] = {
                'id': tid,
                'name': data.get('title', tid),
                'type': data.get('category', 'uncategorized'),
                'frequency': data.get('frequency', 'as-needed'),
                'months': data.get('months'),
                'timing_note': data.get('timing_note', ''),
                'description': desc,
                'tags': data.get('tags', []),
                'event': data.get('event'),
                'owner': data.get('owner', 'unknown'),
                'roles': data.get('roles', []),
                'task_url': f'/tasks/{data.get("category", "uncategorized")}/{tid}/',
            }

    print(f'Read {len(tasks_by_id)} task definitions from tasks/**/*.md')

    # ── Step 2: Read role assignments from roles/*/tasks.yaml ──
    task_files = sorted(ROLES_DIR.glob('*/tasks.yaml')) + sorted(ROLES_DIR.glob('*/*/tasks.yaml'))

    role_assignments = {}  # tid -> {owner: role_id, roles: [role_ids]}

    for tf in task_files:
        role_dir = tf.parent
        role_id = get_role_id(role_dir)

        data = parse_yaml_simple(str(tf))
        if not data or not data.get('tasks'):
            continue

        for task_ref in data['tasks']:
            tid = task_ref['id']
            role_type = task_ref.get('role', 'involved')

            if tid not in role_assignments:
                role_assignments[tid] = {'owner': None, 'roles': []}

            entry = role_assignments[tid]
            if role_type == 'owner' and entry['owner'] is None:
                entry['owner'] = role_id
            if role_id not in entry['roles']:
                entry['roles'].append(role_id)

    # Merge role assignments into task definitions
    for tid, task in tasks_by_id.items():
        if tid in role_assignments:
            ra = role_assignments[tid]
            if ra['owner']:
                task['owner'] = ra['owner']
            if ra['roles']:
                task['roles'] = ra['roles']

    # Check for role assignments referencing unknown tasks
    for tid in role_assignments:
        if tid not in tasks_by_id:
            warnings.append(f'Role assignment references unknown task "{tid}"')

    # ── Step 3: Read event definitions from events/**/*.md ──
    events_by_id = OrderedDict()
    if EVENTS_DIR.exists():
        for ef in sorted(EVENTS_DIR.glob('**/*.md')):
            if ef.name == 'README.md':
                continue
            data = parse_front_matter(str(ef))
            if not data or 'event_id' not in data:
                continue
            eid = data['event_id']
            if 'category' not in data:
                data['category'] = ef.parent.name
            events_by_id[eid] = data

    # ── Step 4: Write pack-tasks-generated.yaml ──
    with open(OUTPUT, 'w') as f:
        f.write('# Auto-generated from tasks/**/*.md definitions and roles/*/tasks.yaml assignments.\n')
        f.write('# Do not edit directly. Run: python3 scripts/aggregate-tasks.py\n')
        f.write('#\n')
        f.write('# Source: tasks/**/*.md and roles/*/tasks.yaml\n\n')

        # Meta section
        f.write('meta:\n')
        f.write('  scouting_year: "July\u2013June"\n')
        f.write('  pack: "Pack 232"\n')
        f.write('  council: "Twin Rivers Council"\n')
        f.write('  district: "Fort Orange District"\n')
        f.write('  charter_org: "Glenmont Elementary PTA"\n')
        f.write('  generated: true\n\n')

        f.write('tasks:\n')

        for tid, task in tasks_by_id.items():
            owner = task['owner']
            roles = task['roles']

            f.write(f'\n  - id: {tid}\n')
            f.write(f'    name: "{task["name"]}"\n')
            f.write(f'    type: {task["type"]}\n')
            f.write(f'    frequency: {task["frequency"]}\n')

            months = task.get('months')
            if months is None:
                f.write('    months: null\n')
            else:
                f.write(f'    months: {months}\n')

            timing = task.get('timing_note', '')
            f.write(f'    timing_note: "{timing}"\n')
            f.write(f'    owner: {owner}\n')
            f.write(f'    roles: [{", ".join(roles)}]\n')

            desc = task.get('description', '').strip()
            f.write('    description: >\n')
            for line in desc.split('\n'):
                f.write(f'      {line.strip()}\n')

            tags = task.get('tags', [])
            if tags:
                f.write(f'    tags: {tags}\n')

            f.write(f'    task_url: {task["task_url"]}\n')

            event_id = task.get('event')
            if event_id:
                f.write(f'    event: {event_id}\n')
                if event_id in events_by_id:
                    evt = events_by_id[event_id]
                    f.write(f'    event_name: "{evt["title"]}"\n')
                    f.write(f'    event_url: /events/{evt["category"]}/{event_id}/\n')
                else:
                    warnings.append(f'Task "{tid}" references unknown event "{event_id}"')

    print(f'Generated {OUTPUT} with {len(tasks_by_id)} unique tasks')

    # ── Step 5: Build reverse map and write events output ──
    event_tasks = {}
    for tid, task in tasks_by_id.items():
        eid = task.get('event')
        if eid:
            event_tasks.setdefault(eid, []).append(tid)

    with open(EVENTS_OUTPUT, 'w') as f:
        f.write('# Auto-generated from events/**/*.md front matter.\n')
        f.write('# Do not edit directly. Run: python3 scripts/aggregate-tasks.py\n\n')

        f.write('events:\n')

        for eid, evt in events_by_id.items():
            f.write(f'\n  - event_id: {eid}\n')
            f.write(f'    title: "{evt.get("title", eid)}"\n')
            f.write(f'    category: {evt.get("category", "uncategorized")}\n')
            f.write(f'    frequency: {evt.get("frequency", "annual")}\n')

            months = evt.get('months')
            if months is None:
                f.write('    months: null\n')
            else:
                f.write(f'    months: {months}\n')

            timing = evt.get('timing_note', '')
            f.write(f'    timing_note: "{timing}"\n')
            f.write(f'    owner: {evt.get("owner", "unknown")}\n')

            roles = evt.get('roles', [])
            if roles:
                f.write(f'    roles: [{", ".join(str(r) for r in roles)}]\n')
            else:
                f.write('    roles: []\n')

            venue = evt.get('venue', '')
            if venue:
                f.write(f'    venue: "{venue}"\n')

            f.write(f'    url: /events/{evt.get("category", "uncategorized")}/{eid}/\n')

            tasks_for_event = event_tasks.get(eid, [])
            if tasks_for_event:
                f.write(f'    tasks: [{", ".join(tasks_for_event)}]\n')
            else:
                f.write('    tasks: []\n')

    print(f'Generated {EVENTS_OUTPUT} with {len(events_by_id)} events')

    # ── Step 6: Read training definitions from training/**/*.md ──
    training_by_id = OrderedDict()
    if TRAINING_DIR.exists():
        for tf in sorted(TRAINING_DIR.glob('**/*.md')):
            if tf.name == 'README.md':
                continue
            data = parse_front_matter(str(tf))
            # Support both old (course_id) and new (training_id) field names
            cid = data.get('training_id') or data.get('course_id') if data else None
            if not cid:
                continue
            # Determine category from type field, parent dir, or category field
            category = data.get('type') or (tf.parent.name if tf.parent.name != 'training' else 'courses')
            training_code = data.get('training_code') or data.get('course_code', '')
            training_by_id[cid] = {
                'id': cid,
                'name': data.get('title', cid),
                'course_code': training_code,
                'category': category,
                'duration': data.get('duration', 0),
                'description': data.get('description', ''),
                'training_url': f'/training/{category}/{cid}/',
            }

    print(f'Read {len(training_by_id)} training definitions from training/**/*.md')

    # ── Step 7: Read role training assignments from roles/*/training.yaml ──
    training_files = sorted(ROLES_DIR.glob('*/training.yaml'))

    training_role_assignments = {}  # cid -> [{role, status}]

    for tf in training_files:
        role_dir = tf.parent
        role_id = get_role_id(role_dir)

        data = parse_yaml_simple(str(tf))
        if not data or not data.get('training'):
            continue

        for ref in data['training']:
            cid = ref['id']
            status = ref.get('status', 'required')

            if cid not in training_role_assignments:
                training_role_assignments[cid] = []

            training_role_assignments[cid].append({
                'role': role_id,
                'status': status,
            })

    # Check for role assignments referencing unknown training
    for cid in training_role_assignments:
        if cid not in training_by_id:
            warnings.append(f'Role training assignment references unknown course "{cid}"')

    # ── Step 8: Write pack-training-generated.yaml ──
    with open(TRAINING_OUTPUT, 'w') as f:
        f.write('# Auto-generated from training/**/*.md definitions and roles/*/training.yaml assignments.\n')
        f.write('# Do not edit directly. Run: python3 scripts/aggregate-tasks.py\n\n')

        f.write('training:\n')

        for cid, course in training_by_id.items():
            f.write(f'\n  - id: {cid}\n')
            f.write(f'    name: "{course["name"]}"\n')
            f.write(f'    course_code: "{course["course_code"]}"\n')
            f.write(f'    category: {course["category"]}\n')
            f.write(f'    duration: {course["duration"]}\n')

            desc = course.get('description', '').strip()
            if desc:
                f.write('    description: >\n')
                for line in desc.split('\n'):
                    f.write(f'      {line.strip()}\n')
            else:
                f.write('    description: ""\n')

            f.write(f'    training_url: {course["training_url"]}\n')

            reqs = training_role_assignments.get(cid, [])
            if reqs:
                f.write('    role_requirements:\n')
                for req in reqs:
                    f.write(f'      - role: {req["role"]}\n')
                    f.write(f'        status: {req["status"]}\n')
            else:
                f.write('    role_requirements: []\n')

    print(f'Generated {TRAINING_OUTPUT} with {len(training_by_id)} training courses')

    # Print warnings
    for w in warnings:
        print(f'WARNING: {w}', file=sys.stderr)


if __name__ == '__main__':
    main()
