"""Evaluate training/validation loss.

IMPORTANT: Weco optimizes a SINGLE metric. This script should print exactly one
metric in the format: metric_name: value (e.g., "loss: 0.0523")

Constraint violations (training time, memory, etc.) must exit non-zero
before this evaluator prints the metric.
"""
import time
import importlib.util


def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


optimized = load_module(".weco/optimize.py")

# TODO: Load your validation data
# X_val, y_val = load_validation_data()
X_val = None
y_val = None

# =============================================================================
# CONSTRAINT CHECKS (hard gates - do not emit a metric on failure)
# =============================================================================
# Example: Check training time constraint
# start = time.perf_counter()
# model = optimized.train()
# training_time = time.perf_counter() - start
# max_training_time = 300  # 5 minutes
# if training_time > max_training_time:
#     raise SystemExit("Constraint violated: training time exceeds limit")

# Example: Check for NaN/Inf in outputs
# if torch.isnan(output).any():
#     raise SystemExit("Constraint violated: NaN detected in model output")
# if torch.isinf(output).any():
#     raise SystemExit("Constraint violated: Inf detected in model output")

# =============================================================================
# LOSS MEASUREMENT (the single metric to optimize)
# =============================================================================
# TODO: Replace with your loss computation function
loss = optimized.compute_loss(X_val, y_val)

print(f"loss: {loss:.6f}")
