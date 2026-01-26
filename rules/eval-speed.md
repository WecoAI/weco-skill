---
name: eval-speed
description: Speed/performance evaluation template
metadata:
  tags: speed, speedup, performance, benchmark, latency
---

## Template

See [assets/evaluate-speed.py](../assets/evaluate-speed.py) for the complete template.

```python
"""Evaluate performance improvement."""
import time
import importlib.util


def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def benchmark(func, inputs, n_warmup=10, n_iterations=100):
    """Benchmark a function with warmup iterations."""
    for _ in range(n_warmup):
        func(*inputs)
    start = time.perf_counter()
    for _ in range(n_iterations):
        func(*inputs)
    return (time.perf_counter() - start) / n_iterations


baseline = load_module(".weco/baseline.py")
optimized = load_module(".weco/optimize.py")

# TODO: Define test inputs for your function
test_inputs = ()

# CORRECTNESS CHECK
baseline_result = baseline.TARGET_FUNCTION(*test_inputs)
optimized_result = optimized.TARGET_FUNCTION(*test_inputs)

if baseline_result != optimized_result:
    print(f"Constraint violated: output differs from baseline")

# PERFORMANCE MEASUREMENT
baseline_time = benchmark(baseline.TARGET_FUNCTION, test_inputs)
optimized_time = benchmark(optimized.TARGET_FUNCTION, test_inputs)

speedup = baseline_time / optimized_time
print(f"speedup: {speedup:.4f}")
```

## Customization Required

1. Replace `TARGET_FUNCTION` with your actual function name
2. Define `test_inputs` with realistic test data
3. Adjust `n_warmup` and `n_iterations` for your use case
4. Modify correctness check for your output type (use tolerance for floats)

## Best Practices

- Use realistic input sizes
- Include warmup iterations to avoid cold-start effects
- Run multiple iterations for stable measurements
- Always verify correctness before measuring speed
- Use `time.perf_counter()` for accurate timing
