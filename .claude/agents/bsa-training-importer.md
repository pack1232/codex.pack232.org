---
name: bsa-training-importer
description: Import BSA training catalog and regenerate all training files
allowed-tools: Bash, Read, Glob, Skill
---

# BSA Training Importer

Orchestrate the full BSA training import pipeline: fetch from API, generate markdown files, and rebuild the data layer.

## Pre-flight: Token Check

Before running any skills, check that `$BSA_SESSION_TOKEN` is set:

```bash
echo "${BSA_SESSION_TOKEN:?not set}" > /dev/null
```

If the variable is not set, print this message and **STOP**:

```
Error: BSA_SESSION_TOKEN is not set.

To get your session token:
1. Log in at https://training.scouting.org
2. Open DevTools (F12) → Application → Cookies
3. Copy the zanma_sid cookie value
4. export BSA_SESSION_TOKEN=<value>

See docs/agents/bsa-training-importer.md for full instructions.
```

## Step 1: Fetch

Invoke the `bsa-training-fetch` skill.

- If it fails with a 401 error → report expired token, reference docs/agents/bsa-training-importer.md, and **STOP**.
- If any other error → report the error and **STOP**.
- On success, note the total items fetched and breakdown by type.

## Step 2: Generate

Invoke the `bsa-training-generate` skill.

- If `_data/bsa-training-catalog-raw.json` is missing → tell user to re-run fetch and **STOP**.
- On success, note the counts per type (courses, learning plans, programs) and role training file count.

## Step 3: Aggregate

Invoke the `bsa-training-aggregate` skill.

- Note the training count and any warnings from the output.

## Summary

After all steps complete, print a results summary:

```
BSA Training Import Complete
─────────────────────────────
Total items fetched:         <N>
  Courses:                   <N>
  Learning plans:            <N>
  Programs:                  <N>
Files generated:             <N>
Role training.yaml updated:  <N>
Data layer rebuilt:          Yes
Warnings:                    <any warnings or "None">

Run `git status` to review changes, then commit when ready.
```
