#!/usr/bin/env python3
"""
PII Scrubbing Script for Pack Codex → JustOneHourPerWeek migration.

Modes:
  --report   Dry-run: prints what would change without modifying files.
  --apply    Applies all scrubbing changes in-place.

Scope: roles/, tasks/, events/, _data/org-chart.yml, org-chart.md, index.md
Skip:  docs/, training/ (already universal BSA content)
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "scrub-config.yaml"


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


# ── YAML org-chart scrubbing ──────────────────────────────────────────────


def scrub_org_chart_yaml(config, dry_run=True):
    """Remove holder: fields, set vacant: true, scrub charter_org."""
    path = ROOT / "_data" / "org-chart.yml"
    if not path.exists():
        return []

    with open(path) as f:
        data = yaml.safe_load(f)

    changes = []

    # Scrub charter_org
    if "charter_org" in data:
        old = data["charter_org"]
        if old != "Charter Organization":
            changes.append(f"  charter_org: '{old}' → 'Charter Organization'")
            if not dry_run:
                data["charter_org"] = "Charter Organization"

    # Recursively scrub roles
    def scrub_roles(roles, path_prefix=""):
        for role in roles:
            role_path = f"{path_prefix}/{role.get('id', '?')}"
            if "holder" in role:
                changes.append(f"  Remove holder '{role['holder']}' from {role_path}")
                if not dry_run:
                    del role["holder"]
                    role["vacant"] = True
            if "children" in role:
                scrub_roles(role["children"], role_path)

    if "roles" in data:
        scrub_roles(data["roles"])

    if not dry_run and changes:
        with open(path, "w") as f:
            f.write("# Organization Chart Data\n")
            f.write("# Update this file when roles change — the org chart regenerates automatically.\n\n")
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return changes


# ── Mermaid org-chart scrubbing ───────────────────────────────────────────


def scrub_org_chart_mermaid(config, dry_run=True):
    """Remove personal names from mermaid diagram nodes."""
    path = ROOT / "org-chart.md"
    if not path.exists():
        return []

    with open(path) as f:
        content = f.read()

    original = content
    changes = []

    # Scrub charter org in mermaid
    for variation in config.get("charter_org", {}).get("variations", []):
        if variation in content:
            changes.append(f"  Mermaid: '{variation}' → 'Charter Organization'")
            if not dry_run:
                content = content.replace(variation, "Charter Organization")

    exact_charter = config.get("charter_org", {}).get("exact", "")
    if exact_charter and exact_charter in content:
        changes.append(f"  Mermaid: '{exact_charter}' → 'Charter Organization'")
        if not dry_run:
            content = content.replace(exact_charter, "Charter Organization")

    # Remove "<br>Name" from mermaid node labels
    # Pattern: ["Title<br>Name"] → ["Title"]
    for name in config.get("holder_names", []):
        pattern = re.compile(r"<br>" + re.escape(name), re.IGNORECASE)
        if pattern.search(content):
            changes.append(f"  Mermaid: remove '<br>{name}' from node labels")
            if not dry_run:
                content = pattern.sub("", content)

    # Also handle "Charter Organization" text already in the file with Selkirk
    # Handle the charter node specifically
    if 'charter["Selkirk Fire Department No.2"]' in content:
        changes.append("  Mermaid: charter node label → 'Charter Organization'")
        if not dry_run:
            content = content.replace(
                'charter["Selkirk Fire Department No.2"]',
                'charter["Charter Organization"]',
            )

    if not dry_run and content != original:
        with open(path, "w") as f:
            f.write(content)

    return changes


# ── Current Holder section removal ────────────────────────────────────────


def remove_current_holder_section(text):
    """Remove ## Current Holder section up to next ## or --- or EOF."""
    lines = text.split("\n")
    result = []
    in_holder_section = False
    removed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("## Current Holder"):
            in_holder_section = True
            removed_lines.append(line)
            i += 1
            continue

        if in_holder_section:
            # End of section: next heading or horizontal rule (but skip the first ---)
            if stripped.startswith("## ") or (stripped == "---" and removed_lines):
                in_holder_section = False
                # Don't include the trailing --- that ends the section
                if stripped == "---":
                    i += 1
                    continue
                result.append(line)
            else:
                removed_lines.append(line)
            i += 1
            continue

        result.append(line)
        i += 1

    return "\n".join(result), removed_lines


# ── Coordinator table holder scrubbing ────────────────────────────────────


def scrub_coordinator_tables(text, config):
    """Remove holder names from coordinator position tables."""
    changes = []
    for name in config.get("holder_names", []):
        if name in text:
            # Replace "| Name |" with "| [vacant] |" in table rows
            pattern = re.compile(r"\|\s*" + re.escape(name) + r"\s*\|")
            if pattern.search(text):
                changes.append(f"  Table: '{name}' → '[vacant]'")
                text = pattern.sub("| [vacant] |", text)
    return text, changes


# ── Liquid include removal ────────────────────────────────────────────────


def remove_liquid_includes(text):
    """Remove {% include ... %} Jekyll liquid tags."""
    changes = []
    pattern = re.compile(r"\{%\s*include\s+\S+.*?%\}")
    matches = pattern.findall(text)
    if matches:
        for m in matches:
            changes.append(f"  Remove liquid include: {m}")
        text = pattern.sub("", text)
        # Clean up extra blank lines left behind
        text = re.sub(r"\n{3,}", "\n\n", text)
    return text, changes


# ── Prose replacements ────────────────────────────────────────────────────


def scrub_prose(text, config):
    """Apply prose-level replacements: Pack 232, venues, council/district."""
    changes = []

    # Pack identity — case-sensitive replacements
    for old, new in config.get("pack_identity", {}).items():
        # Don't replace in URLs, front matter fields, or code blocks
        # Use word-boundary matching
        pattern = re.compile(r"(?<![/\w])" + re.escape(old) + r"(?![/\w])")
        if pattern.search(text):
            count = len(pattern.findall(text))
            changes.append(f"  '{old}' → '{new}' ({count} occurrences)")
            text = pattern.sub(new, text)

    # Council/district
    for old, new in config.get("council_district", {}).items():
        if old in text:
            count = text.count(old)
            changes.append(f"  '{old}' → '{new}' ({count} occurrences)")
            text = text.replace(old, new)

    # Charter org prose replacements
    for old, new in config.get("charter_org_prose_replacements", {}).items():
        if old in text:
            count = text.count(old)
            changes.append(f"  '{old}' → '{new}' ({count} occurrences)")
            text = text.replace(old, new)

    # Charter org exact match
    exact = config.get("charter_org", {}).get("exact", "")
    if exact and exact in text:
        count = text.count(exact)
        changes.append(f"  '{exact}' → 'Charter Organization' ({count} occurrences)")
        text = text.replace(exact, "Charter Organization")

    # Venue prose replacements
    for old, new in config.get("venues", {}).get("prose", {}).items():
        if old in text:
            count = text.count(old)
            changes.append(f"  Venue: '{old}' → '{new}' ({count} occurrences)")
            text = text.replace(old, new)

    return text, changes


# ── Front matter venue scrubbing ──────────────────────────────────────────


def scrub_front_matter_venues(text, config):
    """Replace venue values in YAML front matter."""
    changes = []
    venue_map = config.get("venues", {}).get("front_matter", {})

    for old, new in venue_map.items():
        pattern = re.compile(r'(venue:\s*["\']?)' + re.escape(old) + r'(["\']?)')
        if pattern.search(text):
            changes.append(f"  Front matter venue: '{old}' → '{new}'")
            text = pattern.sub(r"\g<1>" + new + r"\2", text)

    return text, changes


# ── Email and phone scrubbing ─────────────────────────────────────────────


def scrub_emails_phones(text, config):
    """Remove pack-specific emails and phone numbers from prose."""
    changes = []
    domain = config.get("email_domain", "pack232.com")

    # Emails
    email_pattern = re.compile(r"\b[\w.+-]+@" + re.escape(domain) + r"\b")
    emails = email_pattern.findall(text)
    if emails:
        changes.append(f"  Remove emails: {', '.join(set(emails))}")
        # Remove "| email" or "email |" patterns in holder lines
        text = email_pattern.sub("", text)

    # Phone numbers
    phone_pattern = re.compile(config.get("phone_pattern", r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"))
    phones = phone_pattern.findall(text)
    if phones:
        changes.append(f"  Remove phones: {', '.join(set(phones))}")
        text = phone_pattern.sub("", text)

    # Clean up leftover pipe separators from holder lines: "** | | " → ""
    text = re.sub(r"\*\*\s*\|[\s|]*$", "**", text, flags=re.MULTILINE)
    # Clean up lines that are just pipes and spaces
    text = re.sub(r"^\s*\|\s*\|\s*$", "", text, flags=re.MULTILINE)

    return text, changes


# ── Holder name scrubbing from prose ──────────────────────────────────────


def scrub_holder_names_prose(text, config):
    """Remove holder names that appear in prose outside of Current Holder sections."""
    changes = []
    for name in config.get("holder_names", []):
        # Only replace bold-formatted names (likely role-holder references)
        bold_pattern = re.compile(r"\*\*" + re.escape(name) + r"\*\*")
        if bold_pattern.search(text):
            changes.append(f"  Remove bold name reference: '{name}'")
            text = bold_pattern.sub("**[current holder]**", text)
    return text, changes


# ── Process a single markdown file ────────────────────────────────────────


def process_markdown_file(path, config, dry_run=True):
    """Process a single markdown file through all scrubbing steps."""
    with open(path) as f:
        text = f.read()

    original = text
    all_changes = []

    # 1. Remove Current Holder sections (role READMEs)
    text, removed = remove_current_holder_section(text)
    if removed:
        all_changes.append("  Remove '## Current Holder' section")

    # 2. Scrub coordinator tables
    text, changes = scrub_coordinator_tables(text, config)
    all_changes.extend(changes)

    # 3. Remove liquid includes
    text, changes = remove_liquid_includes(text)
    all_changes.extend(changes)

    # 4. Scrub front matter venues
    text, changes = scrub_front_matter_venues(text, config)
    all_changes.extend(changes)

    # 5. Scrub emails and phones (catch any outside holder sections)
    text, changes = scrub_emails_phones(text, config)
    all_changes.extend(changes)

    # 6. Scrub prose (Pack 232, venues, council/district)
    text, changes = scrub_prose(text, config)
    all_changes.extend(changes)

    # 7. Scrub holder names from prose
    text, changes = scrub_holder_names_prose(text, config)
    all_changes.extend(changes)

    if not dry_run and text != original:
        with open(path, "w") as f:
            f.write(text)

    return all_changes


# ── File discovery ────────────────────────────────────────────────────────


def discover_files():
    """Find all files in scope for scrubbing."""
    files = []

    # Markdown files in roles/, tasks/, events/
    for directory in ["roles", "tasks", "events"]:
        dir_path = ROOT / directory
        if dir_path.exists():
            files.extend(dir_path.rglob("*.md"))

    # Root index.md
    index = ROOT / "index.md"
    if index.exists():
        files.append(index)

    # Shared resources
    shared = ROOT / "roles" / "_shared"
    if shared.exists():
        files.extend(shared.rglob("*.md"))

    # Deduplicate
    files = list(set(files))
    return sorted(files)


# ── Main ──────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Scrub PII from pack codex content")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true", help="Dry-run: show what would change")
    group.add_argument("--apply", action="store_true", help="Apply scrubbing changes in-place")
    args = parser.parse_args()

    dry_run = args.report
    config = load_config()
    total_changes = 0

    mode_label = "REPORT (dry run)" if dry_run else "APPLYING CHANGES"
    print(f"\n{'='*60}")
    print(f"  PII Scrub — {mode_label}")
    print(f"{'='*60}\n")

    # 1. Org chart YAML
    print("── _data/org-chart.yml ──")
    changes = scrub_org_chart_yaml(config, dry_run)
    if changes:
        for c in changes:
            print(c)
        total_changes += len(changes)
    else:
        print("  (no changes)")

    # 2. Org chart mermaid
    print("\n── org-chart.md (mermaid) ──")
    changes = scrub_org_chart_mermaid(config, dry_run)
    if changes:
        for c in changes:
            print(c)
        total_changes += len(changes)
    else:
        print("  (no changes)")

    # 3. Markdown files
    files = discover_files()
    print(f"\n── Markdown files ({len(files)} files) ──\n")

    for path in files:
        rel = path.relative_to(ROOT)
        changes = process_markdown_file(path, config, dry_run)
        if changes:
            print(f"  {rel}:")
            for c in changes:
                print(f"    {c}")
            total_changes += len(changes)

    # Summary
    print(f"\n{'='*60}")
    print(f"  Total changes: {total_changes}")
    if dry_run:
        print("  Run with --apply to make these changes.")
    else:
        print("  Changes applied successfully.")
    print(f"{'='*60}\n")

    return 0 if total_changes >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
