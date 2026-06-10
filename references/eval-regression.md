---
name: eval-regression
description: Regression task evaluation template
metadata:
  tags: regression, mse, rmse, mae, r2
---

## Template

```python
"""Evaluate regression model performance."""
import numpy as np
import importlib.util


def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


optimized = load_module(".weco/optimize.py")

# =============================================================================
# LOAD DATA
# =============================================================================
# Use a real dataset:
#
# sklearn:
#   from sklearn.datasets import fetch_california_housing, load_diabetes
#   data = fetch_california_housing()
#   X, y = data.data, data.target
#
# Time series:
#   import pandas as pd
#   df = pd.read_csv('data.csv', parse_dates=['date'])
#   X = df[feature_cols].values
#   y = df[target_col].values

# TODO: Load your data
X_val = None
y_val = None

# =============================================================================
# PREDICTIONS
# =============================================================================
predictions = optimized.predict(X_val)

# =============================================================================
# METRICS
# =============================================================================
def mse(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

def rmse(y_true, y_pred):
    return np.sqrt(mse(y_true, y_pred))

def mae(y_true, y_pred):
    return np.mean(np.abs(y_true - y_pred))

def r2(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)

def mape(y_true, y_pred):
    # Avoid division by zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

# =============================================================================
# CHOOSE YOUR METRIC
# =============================================================================
# Pick ONE metric to optimize. Common choices:
#
# - rmse: minimize (same units as target, penalizes large errors)
# - mae: minimize (robust to outliers)
# - r2: maximize (0-1 scale, interpretable)
# - mape: minimize (percentage error, good for forecasting)

metric_value = rmse(y_val, predictions)
print(f"rmse: {metric_value:.4f}")

# Optional: report other metrics for context
print(f"mae: {mae(y_val, predictions):.4f}")
print(f"r2: {r2(y_val, predictions):.4f}")
```

## Choosing a Regression Metric

| Metric | Goal | When to Use |
|--------|------|-------------|
| `rmse` | minimize | Default choice, penalizes large errors |
| `mae` | minimize | When outliers should have less influence |
| `r2` | maximize | When you need a 0-1 scale (explained variance) |
| `mape` | minimize | Forecasting, percentage errors matter |

## Watch Out For

### Scale Issues

If `y` values are large, RMSE will be large. Consider:
- Normalizing targets before evaluation
- Using R² which is scale-invariant
- Using MAPE for percentage-based comparison

### Zero Targets

MAPE fails when `y = 0`. Use SMAPE or filter zeros:

```python
def smape(y_true, y_pred):
    """Symmetric MAPE - handles zeros better."""
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
    diff = np.abs(y_true - y_pred)
    # Avoid 0/0
    mask = denominator > 0
    return np.mean(diff[mask] / denominator[mask]) * 100
```

### Heteroscedastic Errors

If error variance changes with target value, consider weighted metrics or log-transform.
