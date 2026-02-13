---
name: monitor
description: Monitor progress and resume interrupted runs
metadata:
  tags: monitor, progress, resume, logs, dashboard
---

## Check if Running

```bash
ps -p $(cat .weco/run.pid) > /dev/null 2>&1 && echo "Running" || echo "Finished"
```

## View Output

```bash
# Latest 50 lines
tail -50 .weco/run.log

# Follow live output
tail -f .weco/run.log
```

## Stop a Run

```bash
kill $(cat .weco/run.pid)
```

## Dashboard

View optimization progress at: https://dashboard.weco.ai

## Resume Interrupted Runs

If an optimization is interrupted, resume it using the run ID:

```bash
weco resume <run-id> --output plain --apply-change
```

Example:

```bash
weco resume 0002e071-1b67-411f-a514-36947f0c4b31 --output plain --apply-change
```

The run ID can be found in:
- The `.runs/` directory (folder names are run IDs)
- The Weco dashboard
- The original run output

## Resume Options

| Option | Description |
|--------|-------------|
| `run_id` | UUID of the run to resume (required, positional) |
| `--apply-change` | Auto-apply best solution without prompting |
| `--api-key` | Provide API keys for the run's model |
| `--output` | `rich` (interactive) or `plain` (machine-readable) |

## Log Directory

Weco saves logs to `.runs/` by default. Structure:

```
.runs/
└── <run-id>/
    ├── outputs/
    │   ├── step_1.out.txt
    │   ├── step_2.out.txt
    │   └── ...
    └── ...
```

Use `--save-logs` when running to enable detailed step logs.
