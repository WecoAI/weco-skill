---
name: cli-reference
description: Complete CLI options reference
metadata:
  tags: cli, reference, options, commands
---

## Commands

| Command | Description |
|---------|-------------|
| `weco run` | Start a new optimization |
| `weco run status` | Show run status and progress (JSON) |
| `weco run results` | Show results sorted by metric |
| `weco run show` | Show details for a specific step/node |
| `weco run diff` | Show code diff between steps |
| `weco run stop` | Terminate a running optimization |
| `weco run instruct` | Update additional instructions mid-run |
| `weco run review` | Show pending approval nodes (review mode) |
| `weco run revise` | Replace a pending node's code |
| `weco run submit` | Submit a pending node for evaluation |
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
- `gemini` → `gemini-3.1-pro-preview`
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

## weco run status

Show run status and progress as JSON. Use for mid-run health checks.

```bash
weco run status <run-id>
```

Returns JSON with: `run_id`, `status`, `name`, `current_step`, `total_steps`, `best_metric`, `best_step`, `metric_name`, `goal`, `model`, `require_review`, `pending_nodes`.

## weco run results

Show run results sorted by metric. The primary command for structured result access.

```bash
weco run results <run-id> [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--top` | all | Show only top N results |
| `--format` | `json` | `json`, `table`, or `csv` |
| `--plot` | false | Append ASCII sparkline trajectory |
| `--include-code` | false | Include full source code in output |

Examples:

```bash
weco run results <run-id> --top 5 --format json
weco run results <run-id> --plot
weco run results <run-id> --format csv > trajectory.csv
```

## weco run show

Show details for a specific step/node.

```bash
weco run show <run-id> --step <N|best>
```

Returns JSON with: `step`, `metric`, `plan`, `code`, `parent_step`, `node_id`, `status`, `is_buggy`.

## weco run diff

Show unified code diff between steps.

```bash
weco run diff <run-id> --step <N|best> [--against <baseline|parent|step_number>]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--step` | (required) | Step number or `best` |
| `--against` | `baseline` | Compare against: `baseline` (step 0), `parent`, or a step number |

## weco run stop

Terminate a running optimization gracefully. Solution tree is preserved and the run can be resumed.

```bash
weco run stop <run-id>
```

Returns JSON with: `run_id`, `status`, `best_metric`, `best_step`.

## weco run instruct

Update additional instructions for an active run. The optimizer uses these to guide subsequent steps.

```bash
weco run instruct <run-id> "Focus on memory optimization, avoid changing the API"
```

Returns JSON with: `run_id`, `additional_instructions`.

## weco run review

Show nodes awaiting action (pending approval or evaluation).

```bash
weco run review <run-id>
```

Returns JSON with: `run_id`, `require_review`, `pending_nodes` (each with `node_id`, `step`, `plan`, `code`).

## weco run revise

Replace a pending node's code with a new revision. Use when you want to modify Weco's proposed solution before evaluation.

```bash
weco run revise <run-id> --node <node-id> --source <file>
weco run revise <run-id> --node <node-id> --sources <file1> <file2>
```

The backend auto-generates a plan from the code diff. The node's head revision is updated.

## weco run submit

Submit a pending approval node for local evaluation and report results back to the optimizer. This is how agents interact with review-mode runs.

```bash
# Accept Weco's proposal as-is and evaluate it
weco run submit <run-id> --node <node-id>

# Replace code and evaluate in one step (revise + submit)
weco run submit <run-id> --node <node-id> --source <file>

# Override the eval command (when the stored command doesn't match this environment)
weco run submit <run-id> --node <node-id> --eval-command "bash .weco/task/evaluate.sh"
```

| Option | Description |
|--------|-------------|
| `--node` | Node ID to submit (required) |
| `--source` / `--sources` | Optional: provide code (creates revision before submitting) |
| `-c, --eval-command` | Override the eval command stored in the run |

The command: submits the node → claims the execution task → runs the eval command locally → reports the result. Returns JSON with `status` (`"submitted"` or `"eval_failed"`), `metric`, `node_id`, `run_completed` (true when all steps are done), and `execution_output`.

### Review Mode Workflow

```bash
# 1. Start a run in review mode
weco run --require-review --output plain ...

# 2. Check for unevaluated nodes
weco run status <run-id>       # pending_nodes field
weco run review <run-id>       # detailed view with code + plan

# 3a. Accept Weco's proposal
weco run submit <run-id> --node <node-id>

# 3b. Or replace with your own code and submit
weco run submit <run-id> --node <node-id> --source <file>

# 3c. If the stored eval command doesn't work locally
weco run submit <run-id> --node <node-id> --eval-command "bash .weco/task/evaluate.sh"

# 4. Weco generates next candidate → repeat from step 2
```

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

Log a step result to an observed run. **Only log steps that ran successfully and produced a metric***

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
