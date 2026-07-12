---
name: guidelines
description: Important guidelines and constraints for Weco optimization
metadata:
  tags: guidelines, best-practices, constraints, rules
---

## Let Weco Explore Freely

Do NOT add restrictive constraints in `--additional-instructions` unless the user explicitly asks.

**BAD** (you decided this, not the user):
```bash
--additional-instructions "Keep it simple, no ML dependencies"
```

**GOOD** (let Weco explore):
```bash
# No additional instructions - Weco will try any approach
weco run --source ... --eval-command ... --metric speedup --goal maximize
```

Only add constraints if the user specifically requests them:
- "Keep it simple" → Add simplicity constraint
- "No external dependencies" → Add dependency constraint
- "Must be pure Python" → Add language constraint

## Evaluation Script Requirements

### Output Format

On success, the script MUST exit zero and print exactly one finite metric to
stdout in this format:

```
metric_name: value
```

Examples:
```
speedup: 2.50
accuracy: 0.9523
loss: 0.0234
```

### Constraint Violations

Constraint violations MUST fail closed: write a diagnostic to stderr, exit
non-zero immediately, and do not print any metric:

```python
import sys


if output != expected:
    print("Constraint violated: output differs from baseline", file=sys.stderr)
    raise SystemExit(1)
```

Never continue to metric emission after a failed constraint, and never print a
penalty metric such as `correct: 0`. The CLI must also reject non-zero evaluator
exits before parsing output; an in-process evaluator cannot securely isolate
output from optimized code.

## For ML/Accuracy Tasks

### FORBIDDEN: Hardcoded Data

NEVER use hardcoded examples:

```python
# WRONG - hardcoded examples
X_test = ["hello", "spam message", "normal text"]
y_test = [0, 1, 0]
```

### REQUIRED: Real Datasets

ALWAYS use real datasets:

```python
# CORRECT - real dataset
from sklearn.datasets import fetch_20newsgroups
data = fetch_20newsgroups(subset='test')
X_test, y_test = data.data, data.target
```

Dataset sources:
- `sklearn.datasets` - Built-in datasets
- `datasets` (Hugging Face) - NLP datasets
- Direct URLs - CSV downloads
- `kaggle` CLI - Kaggle competitions

## Output Mode

ALWAYS use `--output plain` for automation:

```bash
weco run ... --output plain
```

The `plain` mode produces machine-readable output suitable for log parsing and automation. The `rich` mode is for interactive terminal use only.

## Reviewing Optimization Output

Weco-generated code has not been reviewed. Before applying changes:
- Review the diff to understand what changed
- Verify the evaluation metric genuinely improved
- Check that no unexpected dependencies, network calls, or file operations were introduced
- The agent should always offer the user a chance to review before applying to the project codebase
