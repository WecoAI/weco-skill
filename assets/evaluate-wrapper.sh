#!/usr/bin/env bash
# =============================================================================
# Weco Evaluation Wrapper
# =============================================================================
# This script is the entrypoint for Weco's evaluation. Customize it to set up
# your environment before running the evaluation script.
#
# The evaluation script MUST print the metric in this format:
#   metric_name: value
#   (e.g., "speedup: 2.5" or "accuracy: 0.95")
# =============================================================================

set -e
cd "$(dirname "$0")/.."

# =============================================================================
# ENVIRONMENT SETUP - Uncomment/modify the appropriate section for your setup
# =============================================================================

# --- Python with uv (recommended for Python projects) ---
# uv run python .weco/evaluate.py

# --- Python with virtualenv ---
# source .venv/bin/activate
# python .weco/evaluate.py

# --- Python with conda ---
# eval "$(conda shell.bash hook)"
# conda activate myenv
# python .weco/evaluate.py

# --- Python with Poetry ---
# poetry run python .weco/evaluate.py

# --- Node.js ---
# node .weco/evaluate.js

# --- Node.js with npm/yarn ---
# npm run evaluate
# yarn evaluate

# --- Rust ---
# cargo run --release --bin evaluate

# --- Go ---
# go run .weco/evaluate.go

# --- Custom command ---
# ./my_custom_eval.sh

# =============================================================================
# DEFAULT: Plain Python (modify above if this doesn't work for your setup)
# =============================================================================
python .weco/evaluate.py
