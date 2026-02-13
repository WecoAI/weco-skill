---
name: numerical-correctness
description: Verifying correctness for numerical and floating-point code
metadata:
  tags: correctness, floating-point, tolerance, numerical, validation
---

## The Problem

This code is BROKEN for floating-point results:

```python
# WRONG - will almost always fail for floats
if baseline_result != optimized_result:
    print("Constraint violated")
```

Floating-point arithmetic is not exact. `0.1 + 0.2 != 0.3` in most languages.

## Tolerance-Based Comparison

### For Scalars

```python
import math

def is_close(a, b, rel_tol=1e-9, abs_tol=1e-12):
    """Check if two floats are approximately equal."""
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

# Usage
if not is_close(baseline_result, optimized_result, rel_tol=1e-5):
    print(f"Constraint violated: result differs by {abs(baseline_result - optimized_result):.2e}")
```

### For NumPy Arrays

```python
import numpy as np

def arrays_close(a, b, rtol=1e-5, atol=1e-8):
    """Check if two arrays are approximately equal."""
    return np.allclose(a, b, rtol=rtol, atol=atol)

# Usage
if not arrays_close(baseline_result, optimized_result):
    diff = np.abs(baseline_result - optimized_result)
    print(f"Constraint violated: max diff = {diff.max():.2e}, mean diff = {diff.mean():.2e}")
```

### For PyTorch Tensors

```python
import torch

def tensors_close(a, b, rtol=1e-5, atol=1e-8):
    """Check if two tensors are approximately equal."""
    return torch.allclose(a, b, rtol=rtol, atol=atol)

# Also check for NaN/Inf
if torch.isnan(optimized_result).any():
    print("Constraint violated: NaN in output")
if torch.isinf(optimized_result).any():
    print("Constraint violated: Inf in output")
```

## Choosing Tolerances

| Precision | Relative Tolerance | Absolute Tolerance | Use Case |
|-----------|-------------------|-------------------|----------|
| FP64 exact | 1e-14 | 1e-15 | Scientific computing |
| FP64 typical | 1e-9 | 1e-12 | General numerics |
| FP32 | 1e-5 | 1e-8 | ML inference |
| FP16/BF16 | 1e-2 | 1e-3 | Mixed precision ML |
| Quantized | 1e-1 | 1e-1 | INT8 inference |

## Relative vs Absolute Tolerance

- **Relative tolerance** (`rtol`): Error as fraction of value. Good for large values.
- **Absolute tolerance** (`atol`): Fixed error bound. Good for values near zero.

The comparison is: `|a - b| <= atol + rtol * |b|`

## Special Cases

### Results with Different Shapes

```python
if baseline_result.shape != optimized_result.shape:
    print(f"Constraint violated: shape mismatch {baseline_result.shape} vs {optimized_result.shape}")
```

### Stochastic Algorithms

For algorithms with randomness, fix seeds or compare distributions:

```python
import numpy as np

# Option 1: Fix seeds
np.random.seed(42)
torch.manual_seed(42)

# Option 2: Compare over multiple runs
baseline_results = [baseline.func(x) for _ in range(100)]
optimized_results = [optimized.func(x) for _ in range(100)]

baseline_mean = np.mean(baseline_results)
optimized_mean = np.mean(optimized_results)

# Use statistical test
from scipy import stats
_, p_value = stats.ttest_ind(baseline_results, optimized_results)
if p_value < 0.05:
    print(f"Constraint violated: statistically different outputs (p={p_value:.4f})")
```

### Sorting and Ordering

For algorithms that produce unordered results:

```python
# Sort before comparing
baseline_sorted = np.sort(baseline_result)
optimized_sorted = np.sort(optimized_result)
if not arrays_close(baseline_sorted, optimized_sorted):
    print("Constraint violated: different values (ignoring order)")
```
