# codex.scoutosia.com

Private backend intelligence layer for the Scoutosia platform. This is the **single source of truth** for all structured content — it is NOT a website.

## Architecture

```
codex.scoutosia.com (this repo — content only, no build infrastructure)
  ├── syncs to → orgstrong/www.justonehourperweek.com (adult volunteer site, Astro Starlight)
  ├── syncs to → orgstrong/www.askyourspl.com (youth leadership site, Astro Starlight)
  └── syncs to → orgstrong/scoutosia.com (platform hub, future)
```

Content flows **one direction**: codex → consumer sites, via `fractary-codex` sync. Consumer sites have their own Astro build stacks, components, and deploy pipelines. This repo has NO site build infrastructure — no Astro, no Node dependencies for building, no Cloudflare Pages deployment.

## Repo Structure

- `content/` — All markdown content organized by type (roles, tasks, events, training)
- `_data/` — Runtime data files (org-chart.yml, generated YAMLs from scripts)
- `data/` — Data documentation
- `scripts/` — Python scripts for validation, export, aggregation
- `docs/` — Reference documents, resources, and guides
- `.fractary/config.yaml` — Defines sync targets and path mappings to consumer repos

## Content Types

Each content file has frontmatter identifying its type:
- **Roles** (`content/roles/`): `role_id`, `audience` (adult/youth/both), `works_with`, `training_required`
- **Tasks** (`content/tasks/`): `task_id`, `category`, `frequency`, `owner`, `roles`
- **Events** (`content/events/`): `event_id`, `category`, `months`, `venue`
- **Training** (`content/training/`): `training_id`, `training_code`, `type` (courses/learning-plans/programs)

## Key Commands

```bash
python3 scripts/validate-content.py          # Validate all content schemas
python3 scripts/validate-content.py --strict # Fail on warnings too
python3 scripts/export-codex.py -o dist/codex # Export content pack
python3 scripts/aggregate-tasks.py           # Regenerate task YAML from content
```

## What Does NOT Belong Here

- Astro components, layouts, styles, or site configs — those go in consumer site repos
- Node.js build tooling (package-lock, pnpm-lock, node_modules)
- Cloudflare Pages deployment configs
- Any presentation-layer concerns

## GitHub Org

All repos are under the `orgstrong` GitHub organization. This repo is at `orgstrong/codex.scoutosia.com`. The content is part of the Scoutosia vertical within the broader Grouperly umbrella.

## Content Sync Targets

See `.fractary/config.yaml` for the full mapping. Summary:
- **www.justonehourperweek.com** gets: ALL of `content/` + `_data/`
- **www.askyourspl.com** gets: `content/roles/youth/`, `content/roles/shared/`, `content/roles/_shared/`, `content/training/`, subset of `_data/`
