---
name: benchmarking
description: Statistically sound benchmarking methodology
metadata:
  tags: benchmark, statistics, variance, measurement, timing
---

## The Problem with Naive Benchmarking

Simple timing loops produce unreliable measurements due to:
- **CPU frequency scaling**: Turbo boost varies based on thermal state
- **Cache effects**: First runs are slower (cold cache)
- **GC pressure**: Python's garbage collector causes random pauses
- **Background processes**: System load affects measurements
- **Measurement overhead**: The timing code itself takes time

## Minimum Requirements for Reliable Benchmarks

### 1. Use Multiple Runs and Report Statistics

```python
import statistics
import time

def benchmark(func, inputs, n_warmup=10, n_iterations=100, n_runs=5):
    """Run benchmark multiple times and return statistics."""
    run_times = []

    for run in range(n_runs):
        # Warmup for each run
        for _ in range(n_warmup):
            func(*inputs)

        # Measure
        start = time.perf_counter()
        for _ in range(n_iterations):
            func(*inputs)
        elapsed = (time.perf_counter() - start) / n_iterations
        run_times.append(elapsed)

    return {
        'mean': statistics.mean(run_times),
        'median': statistics.median(run_times),
        'stdev': statistics.stdev(run_times) if len(run_times) > 1 else 0,
        'min': min(run_times),
        'max': max(run_times),
    }
```

### 2. Check for Statistical Significance

A 1.05x speedup might be noise. Require meaningful improvement:

```python
baseline_stats = benchmark(baseline.func, inputs)
optimized_stats = benchmark(optimized.func, inputs)

speedup = baseline_stats['mean'] / optimized_stats['mean']

# Check if improvement is outside noise range
# Use coefficient of variation (CV) to assess reliability
cv = baseline_stats['stdev'] / baseline_stats['mean']
if cv > 0.1:  # >10% variation
    print(f"Warning: high variance (CV={cv:.2%}), results may be unreliable")

# Only report speedup if statistically meaningful
if speedup > 1.0 + 2 * cv:  # Outside 2-sigma noise
    print(f"speedup: {speedup:.4f}")
else:
    print(f"speedup: 1.0000")  # Not enough improvement to be confident
```

### 3. Isolate Cache Effects

```python
def benchmark_cold_cache(func, inputs_generator, n_iterations=20):
    """Benchmark with cold cache by using fresh inputs each time."""
    times = []
    for _ in range(n_iterations):
        fresh_inputs = inputs_generator()  # Generate new data each time
        start = time.perf_counter()
        func(*fresh_inputs)
        times.append(time.perf_counter() - start)
    return statistics.median(times)
```

### 4. Use Professional Benchmarking Tools

For serious performance work, use established tools:

```python
# Option 1: timeit (stdlib)
import timeit
time_per_call = timeit.timeit(
    lambda: func(*inputs),
    number=1000
) / 1000

# Option 2: pyperf (more rigorous)
# pip install pyperf
import pyperf
runner = pyperf.Runner()
runner.bench_func('my_benchmark', func, *inputs)
```

## GPU Benchmarking

CPU timing is WRONG for GPU code. Use CUDA events:

```python
import torch

def benchmark_cuda(func, inputs, n_warmup=10, n_iterations=100):
    """Benchmark GPU code using CUDA events."""
    # Warmup
    for _ in range(n_warmup):
        func(*inputs)

    torch.cuda.synchronize()

    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)

    start_event.record()
    for _ in range(n_iterations):
        func(*inputs)
    end_event.record()

    torch.cuda.synchronize()

    elapsed_ms = start_event.elapsed_time(end_event) / n_iterations
    return elapsed_ms
```

## What to Report

Always include in your evaluation output:

```python
print(f"speedup: {speedup:.4f}")
print(f"baseline_mean_ms: {baseline_stats['mean']*1000:.4f}")
print(f"optimized_mean_ms: {optimized_stats['mean']*1000:.4f}")
print(f"baseline_stdev_ms: {baseline_stats['stdev']*1000:.4f}")
print(f"optimized_stdev_ms: {optimized_stats['stdev']*1000:.4f}")
```

Note: Only `speedup` will be used as the metric, but the additional info helps diagnose issues.
