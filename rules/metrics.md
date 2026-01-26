---
name: metrics
description: Choosing metrics and optimization profiles
metadata:
  tags: metrics, profiles, goals, constraints
---

## Optimization Profiles

### API/Production Inference

**Use case**: Model serving via API endpoint

| Metric | Goal | Description |
|--------|------|-------------|
| `latency_p99` | minimize | 99th percentile latency in ms |
| `throughput` | maximize | Requests per second |
| `memory_mb` | minimize | Peak memory usage |

**Tips**: Benchmark with realistic batch sizes, include warm-up iterations.

### Training Speed

**Use case**: Faster model training or fine-tuning

| Metric | Goal | Description |
|--------|------|-------------|
| `speedup` | maximize | Training time improvement ratio |
| `samples_per_second` | maximize | Training throughput |

**Best Practices**:
- Use mixed precision training (FP16/BF16)
- Optimize data loading with prefetching
- Consider `torch.compile()` or JIT compilation
- Use gradient accumulation for larger effective batch sizes

### Model Accuracy

**Use case**: Improve model quality metrics

| Metric | Goal | Description |
|--------|------|-------------|
| `accuracy` | maximize | Classification accuracy |
| `f1_score` | maximize | F1 for imbalanced data |
| `auc_roc` | maximize | Area under ROC curve |
| `loss` | minimize | Validation loss |

**Best Practices**:
- NEVER hardcode predictions or thresholds
- Use real datasets (sklearn, huggingface, kaggle)
- Always split data properly (train/val/test)
- Use cross-validation for small datasets

### GPU Kernel

**Use case**: CUDA/Triton kernel performance

| Metric | Goal | Description |
|--------|------|-------------|
| `kernel_time_ms` | minimize | Kernel execution time |
| `memory_bandwidth` | maximize | GB/s achieved |
| `flops` | maximize | Compute throughput |

**Tips**: Use CUDA events for timing, average over many iterations.

### Code Performance

**Use case**: Speed up CPU-bound code

| Metric | Goal | Description |
|--------|------|-------------|
| `speedup` | maximize | Execution time improvement |
| `execution_time` | minimize | Wall clock time |

**Best Practices**:
- Use vectorized operations (numpy, pandas) instead of loops
- Leverage BLAS/LAPACK for linear algebra
- Consider numba JIT compilation
- Profile before optimizing

### Prompt Engineering

**Use case**: Optimize LLM prompts

| Metric | Goal | Description |
|--------|------|-------------|
| `win_rate` | maximize | Preference vs baseline |
| `task_accuracy` | maximize | Correct outputs |

**Tips**: Use diverse test cases, consider LLM-as-judge evaluation.

### Model Compression

**Use case**: Reduce model size while maintaining quality

| Metric | Goal | Description |
|--------|------|-------------|
| `model_size_mb` | minimize | Model file size |
| `accuracy_retention` | maximize | % of original accuracy |

**Tips**: Compare against uncompressed baseline, test on edge cases.
