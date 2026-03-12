# codex.scoutosia.com

Private backend intelligence layer for the Scoutosia platform. Contains all structured content (roles, tasks, events, training) and runtime data that drives the public-facing sites:

- **[justonehourperweek.com](https://justonehourperweek.com)** — Adult volunteer knowledge base for Cub Scout pack leaders
- **[askyourspl.com](https://askyourspl.com)** — Youth leadership guide for Scouts BSA troops
- **[scoutosia.com](https://scoutosia.com)** — Platform hub (future)

## Structure

```
content/          # Markdown content (roles, tasks, events, training)
_data/            # Runtime data (org-chart, generated YAMLs)
data/             # Data documentation
scripts/          # Validation, export, aggregation scripts
docs/             # Documentation
```

## Content Sync

Content is synced to consumer site repos via `fractary-codex`:
- `orgstrong/justonehourperweek.com` — all content + data
- `orgstrong/askyourspl.com` — youth/shared roles + training subset

## Scripts

```bash
# Validate all content schemas
python3 scripts/validate-content.py

# Export content pack
python3 scripts/export-codex.py -o dist/codex
```
