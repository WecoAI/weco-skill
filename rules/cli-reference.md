---
name: cli-reference
description: Complete CLI options reference
metadata:
  tags: cli, reference, options, commands
---

## Commands

| Command | Description |
|---------|-------------|
| `weco run` | Run code optimization |
| `weco resume` | Resume an interrupted run |
| `weco login` | Authenticate via browser |
| `weco logout` | Clear saved API key |
| `weco credits` | Manage credits (balance, topup, autotopup) |

## weco run

### Required Options

| Option | Description |
|--------|-------------|
| `-s, --source` | Path to source file to optimize |
| `-c, --eval-command` | Command to run for evaluation |
| `-m, --metric` | Metric name printed by eval command |
| `-g, --goal` | `maximize`/`max` or `minimize`/`min` |

### Optional Options

| Option | Default | Description |
|--------|---------|-------------|
| `-n, --steps` | 100 | Number of optimization steps |
| `-M, --model` | `o4-mini` | Model to use |
| `-l, --log-dir` | `.runs` | Directory for logs and results |
| `-i, --additional-instructions` | - | Extra guidance (text or file path) |
| `--eval-timeout` | - | Timeout in seconds per evaluation |
| `--save-logs` | false | Save step outputs to `.runs/<id>/outputs/` |
| `--apply-change` | false | Auto-apply best solution |
| `--require-review` | false | Require manual approval of each change |
| `--api-key` | - | Provider API keys (see below) |
| `--output` | `rich` | `rich` (interactive) or `plain` (machine-readable) |

### API Key Format

```bash
--api-key gemini=KEY openai=KEY anthropic=KEY
```

Supported providers and their default models:
- `gemini` → `gemini-3-pro-preview`
- `openai` → `o4-mini`
- `anthropic` → `claude-opus-4-5`

## weco resume

Resume an interrupted optimization run.

```bash
weco resume <run-id> [options]
```

| Option | Description |
|--------|-------------|
| `run_id` | UUID of the run (required, positional) |
| `--apply-change` | Auto-apply best solution |
| `--api-key` | Provider API keys |
| `--output` | `rich` or `plain` |

## weco credits

```bash
weco credits balance     # Check current balance
weco credits topup       # Purchase additional credits
weco credits autotopup   # Configure automatic top-up
```

## weco login / logout

```bash
weco login   # Authenticate via browser
weco logout  # Clear saved API key
```

## Supported Models

Default: `o4-mini`

See full list at: https://docs.weco.ai/cli/supported-models

## Example: Full Command

```bash
weco run \
  --source .weco/optimize.py \
  --eval-command "bash .weco/evaluate.sh" \
  --metric speedup \
  --goal maximize \
  --steps 50 \
  --model claude-sonnet-4-5 \
  --output plain \
  --apply-change \
  --save-logs \
  --eval-timeout 300 \
  --additional-instructions "Focus on vectorization and SIMD"
```
