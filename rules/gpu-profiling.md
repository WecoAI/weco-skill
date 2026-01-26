---
name: gpu-profiling
description: GPU-specific benchmarking and profiling for CUDA/Triton
metadata:
  tags: gpu, cuda, triton, profiling, nsight, memory
---

## CPU Timing is Wrong for GPU Code

This is WRONG:

```python
start = time.perf_counter()
cuda_kernel(x)
elapsed = time.perf_counter() - start  # WRONG - kernel may not be finished
```

GPU kernels are asynchronous. The CPU continues while the GPU works.

## Correct GPU Timing

### PyTorch

```python
import torch

def benchmark_cuda(func, *args, n_warmup=10, n_iterations=100):
    """Benchmark GPU code using CUDA events."""
    # Warmup (important for GPU - JIT compilation, memory allocation)
    for _ in range(n_warmup):
        func(*args)

    torch.cuda.synchronize()

    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)

    start_event.record()
    for _ in range(n_iterations):
        func(*args)
    end_event.record()

    torch.cuda.synchronize()

    elapsed_ms = start_event.elapsed_time(end_event) / n_iterations
    return elapsed_ms

# Usage
kernel_time_ms = benchmark_cuda(my_cuda_function, input_tensor)
print(f"kernel_time_ms: {kernel_time_ms:.4f}")
```

### Raw CUDA (PyCUDA/CuPy)

```python
import cupy as cp

def benchmark_cupy(func, *args, n_warmup=10, n_iterations=100):
    # Warmup
    for _ in range(n_warmup):
        func(*args)

    cp.cuda.Stream.null.synchronize()

    start = cp.cuda.Event()
    end = cp.cuda.Event()

    start.record()
    for _ in range(n_iterations):
        func(*args)
    end.record()
    end.synchronize()

    elapsed_ms = cp.cuda.get_elapsed_time(start, end) / n_iterations
    return elapsed_ms
```

### Triton

```python
import triton

# Triton has built-in benchmarking
@triton.testing.perf_report(
    triton.testing.Benchmark(
        x_names=['size'],
        x_vals=[2**i for i in range(10, 20)],
        line_arg='provider',
        line_vals=['triton', 'torch'],
        line_names=['Triton', 'PyTorch'],
        ylabel='GB/s',
        plot_name='bandwidth',
    )
)
def benchmark(size, provider):
    # Your benchmark code
    pass
```

## Memory Profiling

GPU memory is often the bottleneck.

### PyTorch Memory Tracking

```python
import torch

torch.cuda.reset_peak_memory_stats()

# Run your code
result = my_function(input_tensor)

peak_memory_mb = torch.cuda.max_memory_allocated() / 1024 / 1024
current_memory_mb = torch.cuda.memory_allocated() / 1024 / 1024

print(f"peak_memory_mb: {peak_memory_mb:.2f}")
print(f"current_memory_mb: {current_memory_mb:.2f}")
```

### Memory Constraint

```python
MAX_MEMORY_MB = 4000  # 4GB limit

peak_memory_mb = torch.cuda.max_memory_allocated() / 1024 / 1024
if peak_memory_mb > MAX_MEMORY_MB:
    print(f"Constraint violated: peak memory {peak_memory_mb:.0f}MB exceeds {MAX_MEMORY_MB}MB")

print(f"kernel_time_ms: {kernel_time_ms:.4f}")
```

## Profiling Tools

For deep analysis beyond simple timing:

### NVIDIA Nsight Systems

```bash
nsys profile -o report python your_script.py
nsys stats report.nsys-rep
```

### NVIDIA Nsight Compute (Kernel Analysis)

```bash
ncu --set full python your_script.py
```

### PyTorch Profiler

```python
from torch.profiler import profile, ProfilerActivity

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
) as prof:
    my_function(input_tensor)

print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))
```

## Complete GPU Evaluation Template

```python
"""Evaluate GPU kernel performance."""
import torch
import importlib.util


def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


baseline = load_module(".weco/baseline.py")
optimized = load_module(".weco/optimize.py")

# Test input - use realistic sizes
size = 4096
x = torch.randn(size, size, device='cuda', dtype=torch.float32)

# Correctness check
torch.cuda.synchronize()
baseline_result = baseline.kernel(x)
optimized_result = optimized.kernel(x)

if not torch.allclose(baseline_result, optimized_result, rtol=1e-3, atol=1e-5):
    max_diff = (baseline_result - optimized_result).abs().max().item()
    print(f"Constraint violated: outputs differ by {max_diff:.2e}")

# Memory check
torch.cuda.reset_peak_memory_stats()
_ = optimized.kernel(x)
peak_mb = torch.cuda.max_memory_allocated() / 1024 / 1024
if peak_mb > 4000:
    print(f"Constraint violated: peak memory {peak_mb:.0f}MB exceeds limit")

# Performance measurement
def benchmark(func, *args, n_warmup=50, n_iter=200):
    for _ in range(n_warmup):
        func(*args)
    torch.cuda.synchronize()

    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)

    start.record()
    for _ in range(n_iter):
        func(*args)
    end.record()
    torch.cuda.synchronize()

    return start.elapsed_time(end) / n_iter

baseline_ms = benchmark(baseline.kernel, x)
optimized_ms = benchmark(optimized.kernel, x)

speedup = baseline_ms / optimized_ms
print(f"speedup: {speedup:.4f}")
print(f"baseline_ms: {baseline_ms:.4f}")
print(f"optimized_ms: {optimized_ms:.4f}")
```
