#!/usr/bin/env python3
"""Aggregate per-role tasks.yaml files into _data/pack-tasks-generated.yaml.

Walks roles/*/tasks.yaml and roles/*/*/tasks.yaml, merges tasks by ID,
and outputs a file compatible with the original pack-tasks.yaml schema
so the Liquid include (role-tasks.html) works unchanged.

Usage: python3 scripts/aggregate-tasks.py
"""

import os
import re
import sys
from collections import OrderedDict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROLES_DIR = REPO_ROOT / 'roles'
OUTPUT = REPO_ROOT / '_data' / 'pack-tasks-generated.yaml'


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


def main():
    tasks_by_id = OrderedDict()
    role_ids_seen = set()

    # Process all tasks.yaml files
    task_files = sorted(ROLES_DIR.glob('*/tasks.yaml')) + sorted(ROLES_DIR.glob('*/*/tasks.yaml'))

    for tf in task_files:
        role_dir = tf.parent
        role_id = get_role_id(role_dir)
        role_ids_seen.add(role_id)

        data = parse_yaml_simple(str(tf))
        if not data or not data.get('tasks'):
            continue

        for task in data['tasks']:
            tid = task['id']
            role_type = task.get('role', 'involved')

            if tid not in tasks_by_id:
                tasks_by_id[tid] = {
                    'task': task,
                    'owner': None,
                    'roles': [],
                }

            entry = tasks_by_id[tid]
            if role_type == 'owner' and entry['owner'] is None:
                entry['owner'] = role_id
            if role_id not in entry['roles']:
                entry['roles'].append(role_id)

    # Write output
    with open(OUTPUT, 'w') as f:
        f.write('# Auto-generated from per-role tasks.yaml files.\n')
        f.write('# Do not edit directly. Run: python3 scripts/aggregate-tasks.py\n')
        f.write('#\n')
        f.write('# Source: roles/*/tasks.yaml and roles/*/*/tasks.yaml\n\n')

        # Meta section
        f.write('meta:\n')
        f.write('  scouting_year: "July\u2013June"\n')
        f.write('  pack: "Pack 232"\n')
        f.write('  council: "Twin Rivers Council"\n')
        f.write('  district: "Fort Orange District"\n')
        f.write('  charter_org: "Glenmont Elementary PTA"\n')
        f.write('  generated: true\n\n')

        f.write('tasks:\n')

        for tid, entry in tasks_by_id.items():
            task = entry['task']
            owner = entry['owner'] or entry['roles'][0] if entry['roles'] else 'unknown'
            roles = entry['roles']

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

    print(f'Generated {OUTPUT} with {len(tasks_by_id)} unique tasks')


if __name__ == '__main__':
    main()
