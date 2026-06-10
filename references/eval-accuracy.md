---
name: eval-accuracy
description: Model accuracy evaluation template
metadata:
  tags: accuracy, ml, classification, f1, precision, recall
---

## Critical Rule

NEVER use hardcoded examples or synthetic data. You MUST use real datasets.

**Data integrity:** When loading data from URLs, prefer well-known, versioned sources (sklearn built-in datasets, pinned Hugging Face dataset versions). If using raw URLs, validate that the downloaded data has the expected format (column count, data types, reasonable value ranges) before processing.

## Template

See [assets/evaluate-accuracy.py](../assets/evaluate-accuracy.py) for the complete template.

```python
"""Evaluate model accuracy."""
import importlib.util


def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


optimized = load_module(".weco/optimize.py")

# LOAD A REAL DATASET - NEVER use hardcoded examples!
#
# Spam detection:
#   import pandas as pd
#   url = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
#   df = pd.read_csv(url, sep='\t', header=None, names=['label', 'text'])
#   X_test, y_test = df['text'].values, (df['label'] == 'spam').values
#
# General classification (sklearn):
#   from sklearn.datasets import fetch_20newsgroups
#   data = fetch_20newsgroups(subset='test', categories=['sci.med', 'sci.space'])
#   X_test, y_test = data.data, data.target
#
# Hugging Face:
#   from datasets import load_dataset
#   dataset = load_dataset("imdb", split="test[:1000]")
#   X_test, y_test = dataset["text"], dataset["label"]

# TODO: Replace with actual dataset loading
X_test = None
y_test = None

predictions = optimized.predict(X_test)
accuracy = (predictions == y_test).mean()

print(f"accuracy: {accuracy:.4f}")
```

## Dataset Sources

- **sklearn.datasets**: For example: `load_iris`, `load_digits`, `fetch_20newsgroups`
- **Hugging Face**: For example: `load_dataset("imdb")`, `load_dataset("sst2")`
- **Kaggle**: Download via `kaggle` CLI or direct URLs
- **UCI ML Repository**: Direct CSV downloads

## Best Practices

- NEVER hardcode predictions, thresholds, or class labels
- Always split data into train/validation/test sets
- Use stratification for imbalanced datasets
- Use cross-validation for small datasets
- Report metrics on held-out test set, not training data
- Consider multiple metrics (accuracy, F1, precision, recall)
