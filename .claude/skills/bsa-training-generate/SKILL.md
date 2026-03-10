---
name: bsa-training-generate
description: Generate training markdown files and role training.yaml from raw BSA course data
allowed-tools: Bash, Read, Glob
---

# BSA Training Generate

Generate training markdown files and role training.yaml files from raw BSA course data.

## Steps

1. **Verify raw data exists**: Check that `_data/bsa-training-catalog-raw.json` exists.
   - If missing, report this error and stop:
     ```
     Error: _data/bsa-training-catalog-raw.json not found.
     Run the bsa-training-fetch skill first to download the catalog from the BSA API.
     ```

2. **Run the generate script**:
   ```bash
   python3 .claude/skills/bsa-training-generate/scripts/generate-training.py
   ```

3. **Report results**: Parse the script output and report:
   - Number of files generated per type (courses, learning plans, programs)
   - Number of role training.yaml files generated
