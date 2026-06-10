"""Evaluate performance improvement.

IMPORTANT: Weco optimizes a SINGLE metric. This script should print exactly one
metric in the format: metric_name: value (e.g., "speedup: 2.50")

Constraint violations (correctness, memory limits, etc.) should be printed as
regular messages - Weco will see them and avoid solutions that violate constraints.
"""
import time
import importlib.util


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
# CORRECTNESS CHECK (constraint - print violations, don't use as metric)
# =============================================================================
# TODO: Replace TARGET_FUNCTION with your actual function name
baseline_result = baseline.TARGET_FUNCTION(*test_inputs)
optimized_result = optimized.TARGET_FUNCTION(*test_inputs)

# TODO: Adjust tolerance and comparison for your use case
tolerance = 1e-5
if baseline_result != optimized_result:  # or use: abs(baseline_result - optimized_result) > tolerance
    print(f"Constraint violated: output differs from baseline (expected {baseline_result}, got {optimized_result})")

# =============================================================================
# PERFORMANCE MEASUREMENT (the single metric to optimize)
# =============================================================================
baseline_time = benchmark(baseline.TARGET_FUNCTION, test_inputs)
optimized_time = benchmark(optimized.TARGET_FUNCTION, test_inputs)

speedup = baseline_time / optimized_time
print(f"speedup: {speedup:.4f}")
