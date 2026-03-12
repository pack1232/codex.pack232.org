---
title: Content Contributor Guide
---

# Content Contributor Guide

This guide documents the content schema for the Just One Hour Per Week knowledge base. All content follows a typed YAML front matter format that enables validation, search, and cross-referencing.

## Content Types

There are four primary content types, each with required front matter fields.

### Roles

Role definitions describe leadership positions. Each role lives in its own directory with an `index.md` file.

**Location**: `content/roles/{adult,shared,youth}/<role-name>/index.md`

**Required front matter**:

```yaml
---
title: "Cubmaster"
role_id: cubmaster          # Stable slug ID (lowercase, hyphens)
audience: adult             # adult | youth | both
---
```

**Optional fields**:

```yaml
unit_type: pack             # pack | troop | crew | any
works_with: [committee-chair, den-leader]
related_youth_roles: [den-chief]
related_adult_roles: [scoutmaster]
training_required: [youth-protection-training]
```

**Role guide sub-pages** (like `facilities.md`, `camping.md`) only need a `title` field. They're supplementary documentation, not role definitions.

### Tasks

Tasks describe recurring or one-time responsibilities assigned to roles.

**Location**: `content/tasks/<category>/<task-name>.md`

**Required front matter**:

```yaml
---
title: "Committee Meeting"
task_id: committee-meeting   # Stable slug ID
category: administrative     # See categories below
frequency: monthly           # annual | monthly | quarterly | ad-hoc | etc.
owner: committee-chair       # Role ID of the primary owner
roles:                       # All roles involved
  - committee-chair
  - cubmaster
  - treasurer
---
```

**Valid categories**: `administrative`, `financial`, `fundraising`, `outdoor`, `program`, `recognition`, `recruitment`, `service`, `training`

**Optional fields**:

```yaml
months: [1, 6]              # Months when this task occurs
timing_note: "First Monday of each month"
event: pack-meeting         # Linked event ID
tags: [committee, governance]
```

### Events

Events describe scheduled pack or troop gatherings.

**Location**: `content/events/<category>/<event-name>.md`

**Required front matter**:

```yaml
---
title: "Pack Meeting"
event_id: pack-meeting       # Stable slug ID
category: program            # See categories below
frequency: monthly
owner: cubmaster             # Role ID of the primary owner
roles:                       # All roles involved
  - cubmaster
  - den-leader
  - advancement-chair
---
```

**Valid categories**: `ceremonies`, `fundraising`, `outdoor`, `outings`, `program`, `recruitment`, `service`

**Optional fields**:

```yaml
months: [9, 10, 11, 12, 1, 2, 3, 4, 5]
timing_note: "3rd Monday of each month"
venue: "Pack meeting location"
```

### Training

Training items represent BSA courses, learning plans, and programs.

**Location**: `content/training/{courses,learning-plans,programs}/<id>.md`

**Required front matter**:

```yaml
---
title: "Youth Protection Training"
training_id: y01             # Stable ID (may be numeric)
type: courses                # courses | learning-plans | programs
---
```

**Optional fields**:

```yaml
training_code: "Y01"
duration: 90                 # Minutes (number or string)
description: "Required training for all BSA adults"
url: "https://training.scouting.org/courses/Y01"
```

## Stable IDs

Every content item has a stable, human-readable ID that never changes:

- `role_id`: e.g., `cubmaster`, `den-leader`, `charter-org-rep`
- `task_id`: e.g., `committee-meeting`, `pack-meeting-planning`
- `event_id`: e.g., `pack-meeting`, `pinewood-derby`
- `training_id`: e.g., `y01`, `sco-450`, `1`

**Rules for IDs**:
- Lowercase letters, digits, and hyphens only
- Must start and end with a letter or digit
- No underscores, no uppercase
- Once assigned, IDs never change (they're used for cross-system references)

## Validation

Content schemas are validated in CI. To run locally:

```bash
python3 scripts/validate-content.py
```

The build (`pnpm build`) also validates via Astro's Zod schemas.

## Export

To export all content as structured JSON for external consumers:

```bash
python3 scripts/export-content.py -o dist/export.json
```

## File Naming

- Role directories: `content/roles/adult/<role-slug>/index.md`
- Task files: `content/tasks/<category>/<task-slug>.md`
- Event files: `content/events/<category>/<event-slug>.md`
- Training files: `content/training/<type>/<id>.md`
- Category index pages: `content/<type>/<category>/index.md` (navigation only, no content ID required)
