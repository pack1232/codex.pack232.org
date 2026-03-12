#!/usr/bin/env python3
"""
Export content as structured JSON for Codex sync and external consumers.

Produces a single JSON file with all content items organized by type,
including front matter and markdown body.

Usage:
  python3 scripts/export-content.py                    # Export to stdout
  python3 scripts/export-content.py -o dist/export.json  # Export to file
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"


def parse_front_matter(path):
    """Extract front matter and body from a markdown file."""
    text = path.read_text(errors="replace")
    m = re.match(r"^---\n(.*?)\n---\n*(.*)", text, re.DOTALL)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, m.group(2).strip()


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


def get_content_id(fm, content_type):
    """Extract the stable ID for this content item."""
    id_fields = {
        "role": "role_id",
        "task": "task_id",
        "event": "event_id",
        "training": "training_id",
    }
    field = id_fields.get(content_type)
    return str(fm.get(field, "")) if field else ""


def main():
    parser = argparse.ArgumentParser(description="Export content as JSON")
    parser.add_argument("-o", "--output", help="Output file path")
    args = parser.parse_args()

    export = {
        "version": "1.0.0",
        "schema": "bsa-content-pack",
        "roles": [],
        "tasks": [],
        "events": [],
        "training": [],
    }

    # Jekyll fields to strip from export
    jekyll_fields = {"parent", "nav_order", "nav_exclude", "layout", "permalink", "has_children"}

    for md in sorted(CONTENT.rglob("*.md")):
        content_type = detect_content_type(md)
        if not content_type:
            continue

        fm, body = parse_front_matter(md)
        content_id = get_content_id(fm, content_type)

        # Skip index/category pages without IDs
        if not content_id:
            continue

        # Build clean export item
        item = {k: v for k, v in fm.items() if k not in jekyll_fields}
        item["_id"] = content_id
        item["_type"] = content_type
        item["_path"] = str(md.relative_to(CONTENT))
        item["_body"] = body

        collection = f"{content_type}s" if content_type != "training" else "training"
        export[collection].append(item)

    # Summary
    summary = {t: len(export[t]) for t in ["roles", "tasks", "events", "training"]}

    output = json.dumps(export, indent=2, ensure_ascii=False, default=str)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output)
        print(f"Exported to {args.output}", file=sys.stderr)
    else:
        print(output)

    print(f"Content: {summary}", file=sys.stderr)


if __name__ == "__main__":
    main()
