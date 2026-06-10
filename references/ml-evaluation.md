---
name: ml-evaluation
description: Rigorous ML model evaluation to avoid overfitting and data leakage
metadata:
  tags: ml, overfitting, data-leakage, cross-validation, metrics
---

## The Overfitting Risk

**Critical problem**: When Weco optimizes against a fixed test set, it can overfit to that specific data. The "improved" model may perform worse on new data.

## Mitigation Strategies

### 1. Use a Held-Out Validation Set (Required)

Split your data into THREE sets:
- **Train**: Used by the model to learn
- **Validation**: Used by Weco to measure improvement
- **Test**: NEVER seen during optimization, used for final evaluation

```python
from sklearn.model_selection import train_test_split

# First split: separate test set (never touch during optimization)
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Second split: train and validation
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
)

# Final split: 60% train, 20% val, 20% test
```

In your evaluation script, use ONLY the validation set:

```python
# evaluate.py - use validation set, NOT test set
accuracy = optimized.evaluate(X_val, y_val)
print(f"accuracy: {accuracy:.4f}")
```

### 2. Use Cross-Validation for Small Datasets

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(
    optimized.model, X_val, y_val,
    cv=5, scoring='accuracy'
)

# Report mean to reduce variance
accuracy = scores.mean()
print(f"accuracy: {accuracy:.4f}")
print(f"accuracy_std: {scores.std():.4f}")
```

### 3. Monitor for Overfitting

Track both training and validation metrics:

```python
train_acc = optimized.evaluate(X_train, y_train)
val_acc = optimized.evaluate(X_val, y_val)

gap = train_acc - val_acc
if gap > 0.1:  # 10% gap suggests overfitting
    print(f"Warning: possible overfitting (train={train_acc:.3f}, val={val_acc:.3f})")

print(f"accuracy: {val_acc:.4f}")
```

## Choosing the Right Metric

### Classification

| Scenario | Metric | Reason |
|----------|--------|--------|
| Balanced classes | `accuracy` | Simple, interpretable |
| Imbalanced classes | `f1_score`, `balanced_accuracy` | Accuracy misleading |
| Ranking matters | `auc_roc` | Threshold-independent |
| Cost-sensitive | `precision` or `recall` | Depends on FP vs FN cost |
| Multi-class | `macro_f1`, `micro_f1` | Aggregation strategy matters |

```python
from sklearn.metrics import f1_score, balanced_accuracy_score, roc_auc_score

# For imbalanced data
predictions = optimized.predict(X_val)
f1 = f1_score(y_val, predictions, average='weighted')
print(f"f1_score: {f1:.4f}")

# For probability outputs
probas = optimized.predict_proba(X_val)
auc = roc_auc_score(y_val, probas[:, 1])
print(f"auc_roc: {auc:.4f}")
```

### Regression

| Metric | Goal | Use Case |
|--------|------|----------|
| `mse` | minimize | General, penalizes large errors |
| `rmse` | minimize | Same units as target |
| `mae` | minimize | Robust to outliers |
| `r2` | maximize | Explained variance (0-1 scale) |
| `mape` | minimize | Percentage error |

```python
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

predictions = optimized.predict(X_val)

mse = mean_squared_error(y_val, predictions)
rmse = mse ** 0.5
r2 = r2_score(y_val, predictions)
mae = mean_absolute_error(y_val, predictions)

# Choose ONE as your optimization target
print(f"rmse: {rmse:.4f}")
```

## Reproducibility

ALWAYS set random seeds:

```python
import random
import numpy as np
import torch

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # For full reproducibility (slower)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

set_seed(42)
```

## Final Evaluation Checklist

Before trusting an optimization result:

1. [ ] Used validation set during optimization (not test set)
2. [ ] Evaluated on held-out test set after optimization complete
3. [ ] Checked for overfitting (train vs val gap)
4. [ ] Used appropriate metric for the problem
5. [ ] Set random seeds for reproducibility
6. [ ] Reported confidence intervals or cross-validation scores
