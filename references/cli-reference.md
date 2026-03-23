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
| `weco observe init` | Create a new observed run |
| `weco observe log` | Log a step to an observed run |

## weco run

### Required Options

| Option | Description |
|--------|-------------|
| `-s, --source` | Path to a single source file to optimize (mutually exclusive with `--sources`) |
| `--sources` | Paths to multiple source files to optimize together (mutually exclusive with `-s`). Max 10 files, 200 KB each, 500 KB total. |
| `-c, --eval-command` | Command to run for evaluation |
| `-m, --metric` | Metric name printed by eval command |
| `-g, --goal` | `maximize`/`max` or `minimize`/`min` |

### Optional Options

| Option | Default | Description |
|--------|---------|-------------|
| `-n, --steps` | 100 | Number of optimization steps |
| `-l, --log-dir` | `.runs` | Directory for logs and results |
| `-i, --additional-instructions` | - | Extra guidance (text or file path) |
| `--eval-timeout` | - | Timeout in seconds per evaluation |
| `--save-logs` | false | Save step outputs to `.runs/<id>/outputs/` |
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
| `--api-key` | Provider API keys |
| `--output` | `rich` or `plain` |

## weco credits

```bash
weco credits balance     # Check current balance
weco credits topup       # Purchase additional credits
weco credits autotopup   # Configure automatic top-up
```

## weco observe

Track experiments manually with Weco Observe. Authenticate using `weco login` if needed.

### weco observe init

Create a new observed run. Returns the run ID.

```bash
WECO_RUN_ID=$(weco observe init --name "<run-name>" --metric <metric> --goal <min|max> --source <file>)
```

| Option | Description |
|--------|-------------|
| `--name` | Name for the run |
| `--metric` | Metric name to track |
| `--goal` | `min` or `max` |
| `--source` | Path to source file (captures baseline code as step 0) |

### weco observe log

Log a step result to an observed run.

```bash
weco observe log \
  --run-id "$WECO_RUN_ID" \
  --step <N> \
  --description "<what you tried>" \
  --metrics '{"<metric>": <value>}' \
  --source <file>
```

| Option | Description |
|--------|-------------|
| `--run-id` | Run ID from `observe init` |
| `--step` | Step number (0 for baseline, then 1, 2, 3, ...) |
| `--description` | What was tried in this step |
| `--metrics` | JSON object with metric values |
| `--source` | Path to source file at this step |
| `--parent-step` | Optional. Parent step to branch from. If omitted, chains to the last successful step. |

### Branching

If a step crashed (no result) and you revert, use `--parent-step` to branch from the correct ancestor:

```bash
# Step 3 failed — step 4 branches from step 2 (not 3)
weco observe log --run-id "$WECO_RUN_ID" --step 4 --parent-step 2 \
  --status completed --description "<what you tried>" \
  --metrics '{"<metric>": <value>}' --source <file>
```

## weco login / logout

```bash
weco login   # Authenticate via browser
weco logout  # Clear saved API key
```

## Supported Models

See full list at: https://docs.weco.ai/cli/supported-models

## Example: Full Command

```bash
weco run \
  --source .weco/optimize.py \
  --eval-command "bash .weco/evaluate.sh" \
  --metric speedup \
  --goal maximize \
  --steps 50 \
  --output plain \
  --save-logs \
  --eval-timeout 300 \
  --additional-instructions "Focus on vectorization and SIMD"
```
