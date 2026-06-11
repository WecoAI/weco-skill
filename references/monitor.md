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

## Steer the Optimization (Derive)

To steer a run — whether it has **completed** or is **still running** — **derive** a new run. This is the primary steering mechanism and the preferred choice for redirecting a run in flight: don't wait for it to finish or stop it manually first. Derive inherits the best solution, **stops the current run automatically** (cancels the in-flight step, interrupts active candidates), and gives the optimizer fresh context. Prefer it over `weco run instruct`, which only edits instructions on a live run without resetting context — use `instruct` only for a minor nudge.

Pass steering text via `-i / --additional-instructions` (inline text or path to a file). If omitted, the parent run's instructions are inherited unchanged.

```bash
# Derive from the lineage-best step (global best across ALL runs in the lineage — default)
weco run derive <run-id> --from-step best -i "Focus on memory-efficient data structures" --output plain

# Derive from the best step in just this run
weco run derive <run-id> --from-step run-best -i "Try a different optimizer entirely" --output plain

# Derive from a specific step
weco run derive <run-id> --from-step 7 -i "Explore vectorization" --output plain

# Derive with more steps
weco run derive <run-id> --from-step best -i "Explore vectorization" --steps 50 --output plain
```

Creates a new run using the specified step's code as an inherited baseline (step 0). The inherited baseline is not re-evaluated — no compute is wasted re-measuring a known-good solution. The first real candidate is step 1. The new run gets fresh LLM context. The parent run is stopped automatically. The new run enters the optimization loop immediately.

`--from-step best` finds the **global best across all runs** in the lineage, not just the specified run. Use `--from-step run-best` to derive from the best step in just the specified run.

Returns JSON with: `run_id`, `run_name`, `lineage_id`, `derived_from` (run_id, step, node_id).

**When to derive:**
- User says "try a different approach" or "focus on X"
- User adds constraints: "don't use Y", "only use Z"
- User wants to redirect a run **that is still running** — derive now; it stops the current search for you
- User wants to continue after completion: "keep going", "try more"
- User wants to branch: "try both approaches"

**Dashboard derive requests:** the user can also compose derived runs in the dashboard ("Explore a new path"), possibly several in parallel. You'll receive a `[Dashboard derive request]` message listing the exact `weco run derive` commands — launch each one as a background task without waiting between them (the first becomes the lineage's evaluation consumer; the rest attach and queue behind it), then report the new run IDs and add them ALL to your monitoring loop (`weco run status <run-id>` for each, non-blocking; report bests/completions across the set).

### Derive Options

| Option | Description |
|--------|-------------|
| `run_id` | Parent run UUID (required, positional) |
| `--from-step` | `best` (default: lineage-best = global best across ALL runs), `run-best` (best in the specified run only), or a step number |
| `-i, --additional-instructions` | Steering instructions for the new run (inline text or path to a file). If omitted, the parent run's instructions are inherited. |
| `-n, --steps` | Override step count |
| `--api-key` | API keys in `provider=key` format |
| `--output` | `rich` (interactive) or `plain` (machine-readable) |

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
