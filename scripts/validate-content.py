#!/usr/bin/env python3
"""
Content schema validator for the BSA content pack format.

Validates that all content files in content/ have correct front matter
according to their content type (role, task, event, training).

Usage:
  python3 scripts/validate-content.py          # Validate all content
  python3 scripts/validate-content.py --strict  # Fail on warnings too

Exit codes:
  0 — All valid
  1 — Validation errors found
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

# ── Valid values ──────────────────────────────────────────────────────────

ROLE_AUDIENCES = {"adult", "youth", "both"}
TASK_CATEGORIES = {
    "administrative", "financial", "fundraising", "outdoor",
    "program", "recognition", "recruitment", "service", "training",
}
EVENT_CATEGORIES = {
    "ceremonies", "fundraising", "outdoor", "outings",
    "program", "recruitment", "service",
}
TRAINING_TYPES = {"courses", "learning-plans", "programs"}
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$")

errors = []
warnings = []


def error(path, msg):
    errors.append(f"  ERROR: {path}: {msg}")


def warn(path, msg):
    warnings.append(f"  WARN:  {path}: {msg}")


def is_slug(value):
    return isinstance(value, str) and SLUG_PATTERN.match(value)


def parse_front_matter(path):
    """Extract YAML front matter from a markdown file."""
    text = path.read_text(errors="replace")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        error(path.relative_to(ROOT), "Invalid YAML front matter")
        return None


def is_index_page(path):
    """Index/category pages don't need content-type IDs."""
    return path.name == "index.md" and not any(
        p.name in ("adult", "shared", "youth") for p in path.parents
        if p != CONTENT / "roles"
    )


def detect_content_type(path):
    """Determine content type from file path."""
    rel = path.relative_to(CONTENT)
    parts = rel.parts
    if parts[0] == "roles":
        return "role"
    elif parts[0] == "tasks":
        return "task"
    elif parts[0] == "events":
        return "event"
    elif parts[0] == "training":
        return "training"
    return None


def is_category_index(path, content_type):
    """Check if this is a top-level or category index page."""
    rel = path.relative_to(CONTENT)
    parts = rel.parts
    # Top-level index (e.g., content/roles/index.md, content/tasks/index.md)
    if len(parts) == 2 and parts[1] == "index.md":
        return True
    # Category index (e.g., content/tasks/administrative/index.md)
    if len(parts) == 3 and parts[2] == "index.md" and content_type in ("task", "event", "training"):
        return True
    # Role category index (e.g., content/roles/shared/index.md, content/roles/youth/index.md)
    if content_type == "role" and len(parts) == 3 and parts[2] == "index.md" and parts[1] in ("shared", "youth", "adult"):
        return True
    # Agent pages
    if "agent" in parts:
        return True
    return False


def is_role_definition(path):
    """Role definitions are index.md files with role_id. Sub-pages are guides."""
    return path.name == "index.md"


def validate_role(path, fm):
    """Validate a role definition (index.md with role_id)."""
    rel = path.relative_to(ROOT)
    if "role_id" not in fm:
        error(rel, "Missing role_id")
        return
    if not is_slug(fm["role_id"]):
        error(rel, f"Invalid role_id slug: '{fm['role_id']}'")
    if "audience" not in fm:
        warn(rel, "Missing audience field")
    elif fm["audience"] not in ROLE_AUDIENCES:
        error(rel, f"Invalid audience: '{fm['audience']}' (expected: {ROLE_AUDIENCES})")
    if "title" not in fm:
        error(rel, "Missing title")


def validate_role_guide(path, fm):
    """Validate a role guide/sub-page (non-index .md in a role directory)."""
    rel = path.relative_to(ROOT)
    if "title" not in fm:
        error(rel, "Missing title")


def validate_task(path, fm):
    rel = path.relative_to(ROOT)
    if "task_id" not in fm:
        error(rel, "Missing task_id")
        return
    if not is_slug(fm["task_id"]):
        error(rel, f"Invalid task_id slug: '{fm['task_id']}'")
    if "category" not in fm:
        error(rel, "Missing category")
    elif fm["category"] not in TASK_CATEGORIES:
        error(rel, f"Invalid category: '{fm['category']}' (expected: {TASK_CATEGORIES})")
    if "frequency" not in fm:
        error(rel, "Missing frequency")
    if "owner" not in fm:
        error(rel, "Missing owner")
    if "roles" not in fm:
        warn(rel, "Missing roles array")
    if "title" not in fm:
        error(rel, "Missing title")


def validate_event(path, fm):
    rel = path.relative_to(ROOT)
    if "event_id" not in fm:
        error(rel, "Missing event_id")
        return
    if not is_slug(fm["event_id"]):
        error(rel, f"Invalid event_id slug: '{fm['event_id']}'")
    if "category" not in fm:
        error(rel, "Missing category")
    elif fm["category"] not in EVENT_CATEGORIES:
        error(rel, f"Invalid category: '{fm['category']}' (expected: {EVENT_CATEGORIES})")
    if "frequency" not in fm:
        error(rel, "Missing frequency")
    if "owner" not in fm:
        error(rel, "Missing owner")
    if "title" not in fm:
        error(rel, "Missing title")


def validate_training(path, fm):
    rel = path.relative_to(ROOT)
    if "training_id" not in fm:
        error(rel, "Missing training_id")
        return
    if "type" not in fm:
        error(rel, "Missing type")
    elif fm["type"] not in TRAINING_TYPES:
        error(rel, f"Invalid type: '{fm['type']}' (expected: {TRAINING_TYPES})")
    if "title" not in fm:
        error(rel, "Missing title")


VALIDATORS = {
    "role": validate_role,
    "task": validate_task,
    "event": validate_event,
    "training": validate_training,
}


def main():
    parser = argparse.ArgumentParser(description="Validate content schemas")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    counts = {"role": 0, "role_guide": 0, "task": 0, "event": 0, "training": 0, "skipped": 0}

    print(f"\n{'='*60}")
    print("  Content Schema Validation")
    print(f"{'='*60}\n")

    for md in sorted(CONTENT.rglob("*.md")):
        content_type = detect_content_type(md)
        if not content_type:
            continue

        # Skip category/index pages and agent pages
        if is_category_index(md, content_type):
            counts["skipped"] += 1
            continue

        fm = parse_front_matter(md)
        if fm is None:
            continue

        if content_type == "role":
            if is_role_definition(md):
                validate_role(md, fm)
                counts["role"] += 1
            else:
                validate_role_guide(md, fm)
                counts["role_guide"] += 1
        else:
            validator = VALIDATORS.get(content_type)
            if validator:
                validator(md, fm)
                counts[content_type] += 1

    # Report
    print(f"  Validated:")
    for ct in ("role", "role_guide", "task", "event", "training"):
        label = "role guide" if ct == "role_guide" else ct
        print(f"    {label:>12}: {counts[ct]} files")
    print(f"    {'skipped':>10}: {counts['skipped']} index/category pages")

    if warnings:
        print(f"\n  Warnings ({len(warnings)}):")
        for w in warnings:
            print(w)

    if errors:
        print(f"\n  Errors ({len(errors)}):")
        for e in errors:
            print(e)

    total_issues = len(errors) + (len(warnings) if args.strict else 0)

    print(f"\n{'='*60}")
    if total_issues == 0:
        print("  PASSED — All content valid")
    else:
        print(f"  FAILED — {len(errors)} errors, {len(warnings)} warnings")
    print(f"{'='*60}\n")

    return 1 if total_issues > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
