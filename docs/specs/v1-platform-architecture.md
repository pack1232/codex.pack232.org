# V1 Platform Architecture: Just One Hour Per Week

## Context

Pack 232's codex site has matured into a comprehensive BSA leadership knowledge base (17 roles, 94 tasks, 440+ training courses, events, docs). The vision is to generalize this into a public resource at **justonehourperweek.com** for adult leaders and **askyourspl.com** for youth leaders — helping all units break work into small pieces, define roles clearly, and provide clear guidance for every position.

The core insight: adult and youth leadership are interconnected (Den Chiefs bridge both, SPL/Patrol Leaders interact with adult Scoutmasters), so they need a **single backend repo** that publishes to **two audience-specific frontends** that can cross-link.

### Strategic Context: Three-Layer Vision

This repo exists within a broader product vision:

1. **Open-source content sites** (this repo) — Pure static content: roles, tasks, training, SOPs. Free to serve, community-contributed via PRs. Published at justonehourperweek.com and askyourspl.com.
2. **Scoutosia** (paid) — The interactive layer built on top. AI agents with polished UI, community contribution portal, real unit management (people assigned to roles), login/auth. This is where token costs and per-user features live.
3. **Grouperly** — The generic platform underneath Scoutosia. Scoutosia is Grouperly's BSA vertical, but the platform serves any volunteer organization.

**This repo is one content source** in a multi-source ecosystem that Scoutosia aggregates from. Other sources might include council-specific content, third-party training providers, or unit-contributed materials.

**Lead magnet funnel**: Free static sites provide genuine value (role definitions, task breakdowns, training guides). Every page is a natural on-ramp: "Want AI assistants for each role, community templates, and unit management? Try Scoutosia." The sites drive awareness; Scoutosia captures engaged users.

**Brand independence**: The site brands (justonehourperweek, askyourspl) are intentionally separate from Scoutosia. They stand alone as free resources. The Scoutosia connection is a CTA, not an identity.

---

## Architecture: One Repo, Two Sites, Two Layers

### Layer 1: Content Repository (GitHub — this repo)

The single source of truth. Public repo where contributors submit PRs.

```
justonehourperweek/
├── content/                           # Universal BSA content library
│   ├── roles/
│   │   ├── adult/                     # Adult leader roles (existing, scrubbed)
│   │   │   ├── cubmaster/
│   │   │   ├── committee-chair/
│   │   │   ├── treasurer/
│   │   │   └── ...
│   │   ├── youth/                     # Youth leader roles (new)
│   │   │   ├── senior-patrol-leader/
│   │   │   ├── patrol-leader/
│   │   │   ├── troop-guide/
│   │   │   ├── quartermaster/
│   │   │   └── ...
│   │   └── shared/                    # Roles that bridge both (Den Chief, etc.)
│   │       └── den-chief/
│   ├── tasks/                         # Existing 94 tasks (scrubbed) + youth tasks
│   ├── events/                        # Event templates (scrubbed)
│   ├── training/                      # BSA training catalog (already universal)
│   └── docs/                          # Reference materials (scrubbed)
│
├── sites/
│   ├── justonehourperweek/            # Adult site (static)
│   │   ├── astro.config.ts
│   │   ├── src/pages/
│   │   └── src/components/
│   └── askyourspl/                    # Youth site (static)
│       ├── astro.config.ts
│       ├── src/pages/
│       └── src/components/
│
├── packages/
│   └── shared/
│       ├── content-loader/            # Shared content utilities
│       └── ui/                        # Shared UI components
│
├── scripts/
│   ├── aggregate-tasks.py             # Existing (extended)
│   ├── scrub-pii.py                   # PII removal tool
│   └── build.sh                       # Orchestrates both site builds
│
├── _data/                             # Generated aggregated data
├── .claude/                           # Claude Code skills/agents (for developers)
└── .github/workflows/                 # CI: build + deploy both sites
```

### Layer 2: Static Sites (Astro — replaces Jekyll)

**Why Astro over Jekyll:**
- Astro's [content collections](https://docs.astro.build/en/guides/content-collections/) natively handle markdown+YAML front matter with typed schemas — replacing the custom `aggregate-tasks.py` for querying
- Can build multiple sites from shared content using different configs
- Existing markdown files work as-is (same front matter format)
- Just the Docs equivalent: [Starlight](https://starlight.astro.build/) theme (Astro-native docs theme)

Both sites are **pure static builds** — no SSR, no Workers adapter. `astro build` produces HTML/CSS/JS that deploys to any static host.

**Two sites, one content source:**
- `sites/justonehourperweek/` imports from `content/roles/adult/` + `content/roles/shared/`
- `sites/askyourspl/` imports from `content/roles/youth/` + `content/roles/shared/`
- Cross-site links use absolute URLs (e.g., adult role pages link to related youth roles on askyourspl.com and vice versa)
- Front matter `audiences: [adult, youth, both]` tags enable filtering

**Claude Code agents stay in the repo** via `.claude/` — skills and agents for developers who clone the repo and use Claude Code locally. These are not web-exposed; they're a power-user tool for contributors working on content and code.

---

## Content Schema & Packaging

The content in this repo follows a typed schema designed as a **portable standard**. This matters because the content isn't just for the static sites — it's consumed by Scoutosia and potentially other tools.

### Design Principles

- **Stable IDs**: Every role, task, and training item has a unique, human-readable ID that never changes (e.g., `cubmaster`, `plan-pack-meeting`, `baloo`). These IDs are the primary key for cross-system references.
- **Typed YAML**: Front matter follows strict schemas so content can be validated, queried, and imported programmatically.
- **Separation of concerns**: Content defines "what is this role / task / training" (open, in this repo). "Who fills this role" and "which unit uses this" live in Scoutosia (private, per-unit).

### Example Schema: `role.yaml`

```yaml
id: cubmaster
title: Cubmaster
audience: adult
unit_type: pack
description: >
  The Cubmaster is the pack's program leader, responsible for planning
  and executing den and pack meetings, outdoor activities, and advancement.
responsibilities:
  - Plan and lead monthly pack meetings
  - Coordinate with den leaders on program themes
  - Ensure advancement opportunities are available
works_with:
  - committee-chair
  - den-leader
  - pack-trainer
related_youth_roles:
  - den-chief
training_required:
  - youth-protection-training
  - position-specific-cubmaster
tasks:
  - plan-pack-meeting
  - coordinate-den-themes
  - blue-gold-banquet
```

### Codex Sync

The Fractary Codex plugin provides the mechanism for syncing content from this repo into Scoutosia's catalog. Content is pulled as structured data (not scraped from HTML), maintaining type safety and stable IDs across the boundary.

---

## Content Cross-Linking Between Sites

Adult and youth roles are connected in the content model:

```yaml
# content/roles/adult/cubmaster/README.md front matter
related_youth_roles:
  - den-chief
  - senior-patrol-leader  # for troops

# content/roles/youth/senior-patrol-leader/README.md front matter
related_adult_roles:
  - scoutmaster
  - assistant-scoutmaster
```

Each site renders these as cross-site links:
- On justonehourperweek.com/roles/cubmaster: "Related Youth Roles: [Den Chief](https://askyourspl.com/roles/den-chief)"
- On askyourspl.com/roles/senior-patrol-leader: "Works With: [Scoutmaster](https://justonehourperweek.com/roles/scoutmaster)"

---

## Scoutosia Integration Path

### Multi-Source Content Model

Scoutosia aggregates content from multiple sources:

| Source | Content | License |
|--------|---------|---------|
| This repo (justonehourperweek) | Roles, tasks, training, SOPs | Open source |
| Council-specific repos | Local event templates, council policies | Varies |
| Unit-contributed (via Scoutosia) | SOPs, checklists, templates from real units | CC-BY-SA |
| BSA official | Advancement requirements, policy updates | BSA copyright |

This repo is the **first and reference** content source, but the architecture supports many.

### What Lives Where

| Feature | Open-Source Sites (free) | Scoutosia (paid) |
|---------|--------------------------|-------------------|
| Role definitions & responsibilities | Yes | Yes (imported) |
| Task breakdowns & checklists | Yes | Yes (imported) |
| Training catalog & requirements | Yes | Yes (imported) |
| Event templates | Yes | Yes (imported) |
| AI agents (per-role assistants) | — | Yes |
| Community contribution portal | — | Yes |
| Unit management (people → roles) | — | Yes |
| Login / user accounts | — | Yes |
| File uploads & document storage | — | Yes |
| Cross-unit benchmarking | — | Yes |

### Community Flywheel

Community contributions flow through Scoutosia, not this repo directly. The cycle:
1. Units use Scoutosia with AI agents and content from this repo
2. Units create SOPs, checklists, meeting plans in Scoutosia
3. Best contributions are curated and (optionally) upstreamed back to the open-source repo
4. Improved open content benefits all units, including those on the free tier

---

## PII Scrubbing Strategy

**What gets removed/generalized:**
- `holder:` fields in org-chart.yml → removed (roles defined without holders)
- Personal emails/phones in role READMEs → removed
- "Pack 232" → template variable or removed
- Venue names ("Glenmont Elementary") → generic descriptions
- Council/district names → removed (unit-specific config)

**What stays:**
- Role definitions, responsibilities, requirements
- Task definitions, frequencies, descriptions
- BSA training catalog (already universal)
- Event templates (generalized)

**Pack 232 overlay (private):** The unit can maintain a private `unit-config.yaml` (gitignored) with their specific holders, contacts, venues — rendered locally but never published.

---

## Hosting & Deployment

| Component | Host | Cost |
|-----------|------|------|
| Content repo | GitHub (public) | Free |
| justonehourperweek.com | Cloudflare Pages | Free tier |
| askyourspl.com | Cloudflare Pages | Free tier |
| Domains | 2 domains | ~$25/year |

**Total: ~$2/month** — pure static sites with near-zero hosting cost.

**CI/CD:** GitHub Actions workflow builds both Astro sites on push to main, deploys to Cloudflare Pages.

---

## Migration Phases

### Phase 1: Foundation (scrub + restructure)
1. Run PII scrub on existing content (script + manual review)
2. Restructure `roles/` into `content/roles/adult/`
3. Move `tasks/`, `events/`, `training/` under `content/`
4. Set up Astro project in `sites/justonehourperweek/` pointing at content
5. Configure Starlight theme (Just the Docs equivalent)
6. Deploy to Cloudflare Pages at justonehourperweek.com
7. Keep codex.pack232.org running on Jekyll until ready to sunset

### Phase 2: Content Schema Formalization
1. Define typed YAML schemas for roles, tasks, training, events
2. Assign stable IDs to every content item
3. Add schema validation to CI (build fails on invalid front matter)
4. Structure content for Codex-ready export format
5. Document the content schema as a contributor guide

### Phase 3: Youth Site
1. Create `content/roles/youth/` with SPL, Patrol Leader, Troop Guide, etc.
2. Set up `sites/askyourspl/` with youth-appropriate theming
3. Add cross-site role linking
4. Deploy askyourspl.com

### Phase 4: Scoutosia Content Bridge
1. Configure Codex sync to pull content into Scoutosia catalog
2. Map stable IDs to Scoutosia's internal content model
3. Set up automated sync on content repo changes
4. Validate round-trip: content update → sync → appears in Scoutosia

---

## Verification

- **Phase 1**: `astro build` succeeds for justonehourperweek site; content renders correctly; no PII in output; Lighthouse score comparable to current Jekyll site
- **Phase 2**: All content items have stable IDs; schema validation passes in CI; content exports cleanly as structured data
- **Phase 3**: Both sites build and deploy; cross-site links resolve correctly; youth content renders on askyourspl.com only
- **Phase 4**: Codex sync pulls content into Scoutosia; content updates in this repo appear in Scoutosia within one sync cycle

---

## Decisions Made

1. **Scope**: Both Cub Scouts (packs) AND Scouts BSA (troops) from the start — needed for askyourspl.com to work since SPLs are a troop concept
2. **Framework**: Astro (replacing Jekyll) — enables content collections, multi-site builds, typed schemas
3. **Pure static sites**: No SSR, no auth, no API endpoints on the open-source sites. Near-zero hosting cost.
4. **Interactive features live in Scoutosia**: Web-facing AI agents, community contribution portal, file uploads, and user accounts belong in the paid product, not the open-source sites
5. **Claude Code agents stay in the repo**: `.claude/` skills and agents remain for developers using Claude Code locally — just not exposed via a web UI
6. **AI agents behind Scoutosia paywall**: Per-role AI assistants with polished UI cost tokens per interaction — the paywall funds the API costs and justifies the investment in UX
7. **One content source in a multi-source ecosystem**: This repo is the first and reference source, but Scoutosia aggregates from many sources
8. **Content schema as portable standard**: Typed YAML with stable IDs, designed for programmatic consumption beyond just the static sites
9. **Priority**: Ship the scrubbed public content site (justonehourperweek.com) first as the foundation for everything else

---

## Open Questions

- Should the content schema be a separate spec ("BSA Content Pack Format")?
- Content versioning: SemVer for content packs?
- License: CC-BY-SA for content, MIT for code?
- Do CTAs on the static sites link to Scoutosia? How prominent?
- Can other group types (churches, sports leagues) follow the same content-pack-to-app pattern via Grouperly?
