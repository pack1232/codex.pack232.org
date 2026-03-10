# BSA Training Importer

## Overview

The BSA Training Importer is a Claude Code workflow that fetches the entire training catalog from the Scouting America training API (`training.scouting.org`) and generates markdown files for the Pack 232 Codex site.

The catalog includes three types of training content — courses, learning plans, and programs — all fetched in a single pass. The type of each item is derived from its URL path on training.scouting.org.

The pipeline runs three steps:

1. **Fetch** — Downloads all active training content from the BSA API
2. **Generate** — Creates markdown files (sorted into subdirectories by type) and training.yaml for each role
3. **Aggregate** — Rebuilds the data layer (`pack-training-generated.yaml`)

## Getting the BSA Session Token

The BSA training API requires authentication via a session cookie.

1. Open [training.scouting.org](https://training.scouting.org) in your browser
2. Log in with your my.scouting.org credentials
3. Open DevTools:
   - **Chrome/Edge**: Press `F12` or `Ctrl+Shift+I` → go to **Application** tab → **Cookies** → `training.scouting.org`
   - **Firefox**: Press `F12` → **Storage** tab → **Cookies** → `training.scouting.org`
4. Find the cookie named `zanma_sid` and copy its value
5. The token expires when your browser session ends — you'll need a fresh one each time

## Setting the Token

Set the environment variable **before** launching Claude Code:

```bash
export BSA_SESSION_TOKEN=<your zanma_sid cookie value>
```

Then start Claude Code in the project directory.

## Running the Import

In Claude Code, run:

```
/bsa-training-import
```

The command will:
- Check that your session token is set
- Fetch all training content (courses, learning plans, programs) from the API
- Generate markdown files sorted by type and role training configs
- Rebuild the aggregated data layer
- Print a summary of what was created/updated

## Output Files

| File | Description |
|---|---|
| `_data/bsa-training-catalog-raw.json` | Raw catalog data from the API (all types) |
| `training/README.md` | Training section nav parent |
| `training/courses/README.md` | Courses category listing |
| `training/courses/*.md` | Individual course pages |
| `training/learning-plans/README.md` | Learning plans category listing |
| `training/learning-plans/*.md` | Individual learning plan pages |
| `training/programs/README.md` | Programs category listing |
| `training/programs/*.md` | Individual program pages |
| `roles/*/training.yaml` | Role-specific training requirements |
| `_data/pack-training-generated.yaml` | Aggregated training data layer |

## Manual Execution

If you need to run individual steps outside of Claude Code:

```bash
# Step 1: Fetch (requires token)
export BSA_SESSION_TOKEN=<value>
python3 .claude/skills/bsa-training-fetch/scripts/fetch-training-catalog.py

# Step 2: Generate
python3 .claude/skills/bsa-training-generate/scripts/generate-training.py

# Step 3: Aggregate
python3 scripts/aggregate-tasks.py
```

## Troubleshooting

### "BSA_SESSION_TOKEN is not set"

You need to export the token before starting Claude Code. See "Setting the Token" above.

### 401 Authentication Error

Your session token has expired. Log in again at [training.scouting.org](https://training.scouting.org), copy a fresh `zanma_sid` cookie, and re-export:

```bash
export BSA_SESSION_TOKEN=<new value>
```

### "bsa-training-catalog-raw.json not found"

The generate step requires raw data from the fetch step. Run the full import again, or run the fetch script manually first.

### Python not found

The scripts require Python 3. Install it via your system package manager if not available.
