---
name: eval-training-time
description: Training time evaluation template
metadata:
  tags: training, time, epoch, samples-per-second
---

## Template

See [assets/evaluate-training-time.py](../assets/evaluate-training-time.py) for the complete template.

```python
"""Evaluate training time."""
import time
import os
import importlib.util


def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


optimized = load_module(".weco/optimize.py")

# Clean up cached models to ensure fresh training
MODEL_PATH = getattr(optimized, "MODEL_PATH", "model.pkl")
if os.path.exists(MODEL_PATH):
    os.remove(MODEL_PATH)

# TRAINING TIME MEASUREMENT
start = time.perf_counter()
model = optimized.train_model()
training_time = time.perf_counter() - start

# CONSTRAINT CHECKS
# Example: Check minimum accuracy requirement
# accuracy = evaluate_model(model, X_test, y_test)
# min_accuracy = 0.90
# if accuracy < min_accuracy:
#     print(f"Constraint violated: accuracy {accuracy:.2%} below {min_accuracy:.0%}")

print(f"training_time: {training_time:.4f}")
```

## Goal

For training time, use `--goal minimize`:

```bash
weco run ... --metric training_time --goal minimize
```

## Best Practices

- Clean up cached models before each run
- Add accuracy constraints to prevent quality degradation
- Run for fixed number of steps, not epochs (for comparable timing)
- Consider measuring samples_per_second instead
- Verify loss curves are similar after optimization

## Alternative Metrics

Instead of absolute training time, consider:

- `speedup` - Ratio of baseline to optimized time (goal: maximize)
- `samples_per_second` - Training throughput (goal: maximize)
- `epoch_time` - Time per epoch (goal: minimize)
