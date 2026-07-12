"""Evaluate performance improvement.

IMPORTANT: Weco optimizes a SINGLE metric. This script should print exactly one
metric in the format: metric_name: value (e.g., "speedup: 2.50")

Constraint violations (correctness, memory limits, etc.) must exit non-zero
before this evaluator prints the metric.
"""

import importlib.util
import math
import sys
import time


def fail_constraint(message):
    """Fail without emitting a metric that could score an invalid candidate."""
    print(f"Constraint violated: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def benchmark(func, inputs, n_warmup=10, n_iterations=100):
    """Benchmark a function with warmup iterations."""
    # Warmup
    for _ in range(n_warmup):
        func(*inputs)
    # Measure
    start = time.perf_counter()
    for _ in range(n_iterations):
        func(*inputs)
    return (time.perf_counter() - start) / n_iterations


baseline = load_module(".weco/baseline.py")
optimized = load_module(".weco/optimize.py")

# TODO: Define test inputs for your function
test_inputs = ()

# =============================================================================
# CORRECTNESS CHECK (hard gate - do not emit a metric on failure)
# =============================================================================
# TODO: Replace TARGET_FUNCTION with your actual function name
baseline_result = baseline.TARGET_FUNCTION(*test_inputs)
optimized_result = optimized.TARGET_FUNCTION(*test_inputs)
outputs_match = bool(baseline_result == optimized_result)

# TODO: Adjust tolerance and comparison for your use case
tolerance = 1e-5
if not outputs_match:  # or use: abs(baseline_result - optimized_result) <= tolerance
    fail_constraint("optimized output differs from baseline")

# =============================================================================
# PERFORMANCE MEASUREMENT (the single metric to optimize)
# =============================================================================
baseline_time = benchmark(baseline.TARGET_FUNCTION, test_inputs)
optimized_time = benchmark(optimized.TARGET_FUNCTION, test_inputs)

speedup = baseline_time / optimized_time
if not math.isfinite(speedup) or speedup <= 0:
    fail_constraint("speedup must be finite and positive")

print(f"speedup: {speedup:.4f}")
