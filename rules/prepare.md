---
name: prepare
description: Create the .weco/ directory structure for optimization
metadata:
  tags: prepare, directory, structure, baseline, optimize
---

## Directory Structure

Create this structure in the project root:

```
project/
├── .weco/
│   ├── optimize.py        # The file Weco will modify
│   ├── baseline.py        # Original version (for comparison)
│   ├── evaluate.py        # Evaluation script
│   ├── evaluate.sh        # Shell wrapper for environment setup
│   └── config.json        # Optimization configuration
├── .runs/                  # Weco's log directory (created automatically)
```

## Step 1: Create the directory

```bash
mkdir -p .weco
```

## Step 2: Copy source files

```bash
cp path/to/source.py .weco/optimize.py
cp path/to/source.py .weco/baseline.py
```

The `optimize.py` is what Weco modifies. The `baseline.py` preserves the original for comparison.

## Step 3: Create config.json

```json
{
  "source_file": "/absolute/path/to/original.py",
  "metric": "speedup",
  "goal": "maximize",
  "context": "Description of what the code does",
  "evaluate_command": "bash .weco/evaluate.sh"
}
```

## Step 4: Create the wrapper script

See [assets/evaluate-wrapper.sh](../assets/evaluate-wrapper.sh) for the template.

The wrapper script sets up your environment before running the evaluation:

```bash
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

# Uncomment/modify for your setup:

# --- Python with uv (recommended) ---
# uv run python .weco/evaluate.py

# --- Python with virtualenv ---
# source .venv/bin/activate
# python .weco/evaluate.py

# --- Python with conda ---
# eval "$(conda shell.bash hook)"
# conda activate myenv
# python .weco/evaluate.py

# --- Default: Plain Python ---
python .weco/evaluate.py
```

Make it executable:

```bash
chmod +x .weco/evaluate.sh
```

## Step 5: Create the evaluation script

Choose the appropriate template based on your metric:
- Speed: [rules/eval-speed.md](eval-speed.md)
- Accuracy: [rules/eval-accuracy.md](eval-accuracy.md)
- Loss: [rules/eval-loss.md](eval-loss.md)
- Training time: [rules/eval-training-time.md](eval-training-time.md)
