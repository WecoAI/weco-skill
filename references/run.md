---
name: run
description: Execute optimization with weco run
metadata:
  tags: run, execute, optimization, steps, model
---

## Basic Usage

```bash
weco run \
  --source .weco/optimize.py \
  --eval-command "bash .weco/evaluate.sh" \
  --metric speedup \
  --goal maximize \
  --output plain \
  --apply-change
```

## Required Options

| Option | Description |
|--------|-------------|
| `-s, --source` | Path to source file to optimize |
| `-c, --eval-command` | Command to run for evaluation |
| `-m, --metric` | Metric name printed by eval command |
| `-g, --goal` | `maximize` or `minimize` |

## Common Options

| Option | Description |
|--------|-------------|
| `-n, --steps` | Number of optimization steps (default: 100) |
| `-M, --model` | Model to use (default: `o4-mini`) |
| `--output plain` | Machine-readable output (MUST use for automation) |
| `--apply-change` | Auto-apply best solution without prompting |

## Examples

### With custom steps and model

```bash
weco run \
  --source .weco/optimize.py \
  --eval-command "bash .weco/evaluate.sh" \
  --metric accuracy \
  --goal maximize \
  --steps 50 \
  --model claude-sonnet-4-5 \
  --output plain \
  --apply-change
```

### With additional instructions

```bash
weco run \
  --source .weco/optimize.py \
  --eval-command "bash .weco/evaluate.sh" \
  --metric accuracy \
  --goal maximize \
  --output plain \
  --apply-change \
  --additional-instructions "Focus on feature engineering and ensemble methods"
```

### With evaluation timeout

```bash
weco run \
  --source .weco/optimize.py \
  --eval-command "bash .weco/evaluate.sh" \
  --metric speedup \
  --goal maximize \
  --output plain \
  --apply-change \
  --eval-timeout 3600
```

### Save detailed logs

```bash
weco run \
  --source .weco/optimize.py \
  --eval-command "bash .weco/evaluate.sh" \
  --metric speedup \
  --goal maximize \
  --output plain \
  --apply-change \
  --save-logs
```

Logs saved to `.runs/<run-id>/outputs/step_<n>.out.txt`

### Interactive mode with manual review

```bash
weco run \
  --source .weco/optimize.py \
  --eval-command "bash .weco/evaluate.sh" \
  --metric speedup \
  --goal maximize \
  --require-review
```

## Running in Background

```bash
weco run \
  --source .weco/optimize.py \
  --eval-command "bash .weco/evaluate.sh" \
  --metric speedup \
  --goal maximize \
  --output plain \
  --apply-change \
  > .weco/run.log 2>&1 &

echo $! > .weco/run.pid
```

Monitor with:

```bash
tail -f .weco/run.log
```
