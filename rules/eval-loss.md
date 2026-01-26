---
name: eval-loss
description: Loss/error evaluation template
metadata:
  tags: loss, error, mse, mae, rmse, validation
---

## Template

See [assets/evaluate-loss.py](../assets/evaluate-loss.py) for the complete template.

```python
"""Evaluate training/validation loss."""
import importlib.util


def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


optimized = load_module(".weco/optimize.py")

# TODO: Load your validation data
X_val = None
y_val = None

# CONSTRAINT CHECKS
# Example: Check for NaN/Inf in outputs
# import torch
# output = optimized.forward(X_val)
# if torch.isnan(output).any():
#     print("Constraint violated: NaN detected in model output")
# if torch.isinf(output).any():
#     print("Constraint violated: Inf detected in model output")

loss = optimized.compute_loss(X_val, y_val)
print(f"loss: {loss:.6f}")
```

## Customization Required

1. Load your actual validation data
2. Replace `compute_loss` with your loss computation function
3. Add constraint checks for numerical stability

## Goal

For loss metrics, use `--goal minimize`:

```bash
weco run ... --metric loss --goal minimize
```

## Best Practices

- Use a held-out validation set, not training data
- Check for NaN/Inf values in model outputs
- Consider adding training time constraints
- Watch for overfitting (compare train vs val loss)
