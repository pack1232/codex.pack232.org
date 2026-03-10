---
name: bsa-training-fetch
description: Fetch entire BSA training catalog (courses, learning plans, programs) from training.scouting.org API
allowed-tools: Bash, Read
---

# BSA Training Fetch

Fetch the BSA training catalog from the training.scouting.org API.

## Steps

1. **Verify token**: Check that `$BSA_SESSION_TOKEN` is set.
   - If missing, report this error and stop:
     ```
     Error: BSA_SESSION_TOKEN is not set.
     Set it before launching Claude Code:
       export BSA_SESSION_TOKEN=<your zanma_sid cookie value>
     See docs/agents/bsa-training-importer.md for instructions on obtaining the token.
     ```

2. **Run the fetch script**:
   ```bash
   python3 .claude/skills/bsa-training-fetch/scripts/fetch-training-catalog.py
   ```

3. **Handle errors**:
   - If the script exits with a 401 error, report: "Session token has expired. Log in again at training.scouting.org, copy a fresh zanma_sid cookie, and re-export BSA_SESSION_TOKEN."
   - For other errors, report the error output and stop.

4. **Report results**: Parse the script output and report:
   - Total number of training items fetched
   - Breakdown by type (courses, learning plans, programs)
   - Output file location (`_data/bsa-training-catalog-raw.json`)
