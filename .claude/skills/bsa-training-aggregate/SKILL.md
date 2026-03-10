---
name: bsa-training-aggregate
description: Aggregate training definitions and role assignments into pack-training-generated.yaml
allowed-tools: Bash, Read
---

# BSA Training Aggregate

Aggregate training definitions and role assignments into the generated data layer.

## Steps

1. **Run the aggregate script**:
   ```bash
   python3 scripts/aggregate-tasks.py
   ```

2. **Report results**: Parse the script output and report:
   - Training course count from output
   - Any warnings emitted by the script

3. **Note**: This script also handles tasks and events aggregation. Only the training-related output is relevant for this skill.
