#!/usr/bin/env python3
"""
Export content in Codex-ready format for Scoutosia sync.

Produces a versioned content pack that can be imported by Scoutosia
via the Fractary Codex plugin.

Output structure:
  dist/codex/
    manifest.json        — Pack metadata, version, content counts
    roles.json           — All role definitions
    tasks.json           — All task definitions
    events.json          — All event definitions
    training.json        — All training definitions

Usage:
  python3 scripts/export-codex.py                     # Export to dist/codex/
  python3 scripts/export-codex.py -o /path/to/output  # Custom output dir
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

PACK_ID = "bsa-cub-scout-pack"
PACK_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"


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
    id_fields = {
        "role": "role_id",
        "task": "task_id",
        "event": "event_id",
        "training": "training_id",
    }
    field = id_fields.get(content_type)
    return str(fm.get(field, "")) if field else ""


# Fields to strip from exports (Jekyll-specific)
STRIP_FIELDS = {"parent", "nav_order", "nav_exclude", "layout", "permalink", "has_children"}


def clean_item(fm, body, content_type, path):
    """Build a clean export item."""
    item = {k: v for k, v in fm.items() if k not in STRIP_FIELDS}
    item["_id"] = get_content_id(fm, content_type)
    item["_path"] = str(path.relative_to(CONTENT))
    item["_body_md"] = body
    return item


def main():
    parser = argparse.ArgumentParser(description="Export Codex content pack")
    parser.add_argument("-o", "--output", default="dist/codex", help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    collections = {"roles": [], "tasks": [], "events": [], "training": []}

    for md in sorted(CONTENT.rglob("*.md")):
        content_type = detect_content_type(md)
        if not content_type:
            continue

        fm, body = parse_front_matter(md)
        content_id = get_content_id(fm, content_type)
        if not content_id:
            continue

        item = clean_item(fm, body, content_type, md)
        key = f"{content_type}s" if content_type != "training" else "training"
        collections[key].append(item)

    # Write individual collection files
    for name, items in collections.items():
        path = output_dir / f"{name}.json"
        path.write_text(json.dumps(items, indent=2, ensure_ascii=False, default=str))

    # Write manifest
    manifest = {
        "pack_id": PACK_ID,
        "pack_version": PACK_VERSION,
        "schema_version": SCHEMA_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source": "https://github.com/orgstrong/codex.scoutosia.com",
        "counts": {name: len(items) for name, items in collections.items()},
        "files": [f"{name}.json" for name in collections],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False)
    )

    print(f"Codex content pack exported to {output_dir}/", file=sys.stderr)
    print(f"  Manifest: {PACK_ID} v{PACK_VERSION}", file=sys.stderr)
    for name, items in collections.items():
        print(f"  {name}: {len(items)} items", file=sys.stderr)


if __name__ == "__main__":
    main()
