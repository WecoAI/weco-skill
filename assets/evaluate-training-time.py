"""Evaluate training time.

IMPORTANT: Weco optimizes a SINGLE metric. This script should print exactly one
metric in the format: metric_name: value (e.g., "training_time: 5.23")

Constraint violations (accuracy thresholds, etc.) should be printed as
regular messages - Weco will see them and avoid solutions that violate constraints.
"""
import time
import os
import importlib.util


def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


optimized = load_module(".weco/optimize.py")

# =============================================================================
# SETUP: Clean up cached models to ensure fresh training
# =============================================================================
# TODO: Update MODEL_PATH if your model is saved elsewhere
MODEL_PATH = getattr(optimized, "MODEL_PATH", "model.pkl")
if os.path.exists(MODEL_PATH):
    os.remove(MODEL_PATH)

# =============================================================================
# TRAINING TIME MEASUREMENT (the single metric to optimize)
# =============================================================================
start = time.perf_counter()
# TODO: Replace with your training function
model = optimized.train_model()
training_time = time.perf_counter() - start

# =============================================================================
# CONSTRAINT CHECKS (print violations as regular messages)
# =============================================================================
# TODO: Add accuracy/quality constraints
# Example: Check minimum accuracy requirement
# accuracy = evaluate_model(model, X_test, y_test)
# min_accuracy = 0.90
# if accuracy < min_accuracy:
#     print(f"Constraint violated: accuracy {accuracy:.2%} below {min_accuracy:.0%} threshold")

# Example: Verify model produces valid predictions
# test_input = get_sample_input()
# prediction = model.predict(test_input)
# if prediction is None:
#     print("Constraint violated: model prediction failed")

print(f"training_time: {training_time:.4f}")
