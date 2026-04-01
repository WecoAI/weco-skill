---
name: monitor
description: Monitor progress, steer, and resume runs
metadata:
  tags: monitor, progress, resume, logs, dashboard, status, results
---

## Check Run Status

```bash
weco run status <run-id>
```

Returns JSON with: `run_id`, `status`, `current_step`, `total_steps`, `best_metric`, `best_step`, `metric_name`, `goal`, `model`, `require_review`, `pending_nodes`.

## View Results

```bash
# Top results sorted by metric
weco run results <run-id> --top 5 --format json

# ASCII metric trajectory
weco run results <run-id> --plot

# Export as CSV
weco run results <run-id> --format csv > trajectory.csv

# Include full source code
weco run results <run-id> --top 3 --include-code
```

## Inspect a Step

```bash
# Show details for a specific step
weco run show <run-id> --step 3

# Show details for the best step
weco run show <run-id> --step best
```

Returns JSON with: `step`, `metric`, `plan`, `code`, `parent_step`, `node_id`, `status`, `is_buggy`.

## View Diffs

```bash
# Diff best solution against baseline
weco run diff <run-id> --step best

# Diff against parent step
weco run diff <run-id> --step 5 --against parent

# Diff against a specific step
weco run diff <run-id> --step 5 --against 2
```

## Steer a Running Optimization

Update the optimizer's instructions mid-run:

```bash
weco run instruct <run-id> "Focus on memory optimization, avoid changing the API"
```

## Stop a Run

```bash
weco run stop <run-id>
```

Terminates gracefully. Solution tree is preserved — resume later with `weco resume`.

## Dashboard

View optimization progress at: https://dashboard.weco.ai

## Resume Interrupted Runs

If an optimization is interrupted, resume it using the run ID:

```bash
weco resume <run-id> --output plain
```

The run ID can be found in:
- The `.runs/` directory (folder names are run IDs)
- The Weco dashboard
- The original run output

## Resume Options

| Option | Description |
|--------|-------------|
| `run_id` | UUID of the run to resume (required, positional) |
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
