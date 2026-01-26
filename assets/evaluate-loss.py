"""Evaluate training/validation loss.

IMPORTANT: Weco optimizes a SINGLE metric. This script should print exactly one
metric in the format: metric_name: value (e.g., "loss: 0.0523")

Constraint violations (training time, memory, etc.) should be printed as
regular messages - Weco will see them and avoid solutions that violate constraints.
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
# CONSTRAINT CHECKS (print violations, don't use as metrics)
# =============================================================================
# Example: Check training time constraint
# start = time.perf_counter()
# model = optimized.train()
# training_time = time.perf_counter() - start
# max_training_time = 300  # 5 minutes
# if training_time > max_training_time:
#     print(f"Constraint violated: training took {training_time:.1f}s, exceeds {max_training_time}s limit")

# Example: Check for NaN/Inf in outputs
# if torch.isnan(output).any():
#     print("Constraint violated: NaN detected in model output")
# if torch.isinf(output).any():
#     print("Constraint violated: Inf detected in model output")

# =============================================================================
# LOSS MEASUREMENT (the single metric to optimize)
# =============================================================================
# TODO: Replace with your loss computation function
loss = optimized.compute_loss(X_val, y_val)

print(f"loss: {loss:.6f}")
