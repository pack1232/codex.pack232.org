# data/

Structured data files for Pack 232. Designed to be format-agnostic — these files can be consumed by apps, rendered into PDFs, imported into spreadsheets, or used to generate other views.

## Files

| File | Description |
|---|---|
| `pack-tasks.yaml` | All annual tasks and events the pack must accomplish, with type, owner, and timing |
| `roles.yaml` | All pack roles with metadata (coming soon) |

## Schema

See comments at the top of each YAML file for field definitions.

## Consuming This Data

- **JSON**: `yq -o json pack-tasks.yaml > pack-tasks.json`
- **CSV**: `yq -o csv '.tasks' pack-tasks.yaml > pack-tasks.csv`
- **Filter by month**: `yq '.tasks[] | select(.months[] == 9)' pack-tasks.yaml`
- **Filter by role**: `yq '.tasks[] | select(.owner == "treasurer")' pack-tasks.yaml`
- **Filter by type**: `yq '.tasks[] | select(.type == "financial")' pack-tasks.yaml`
