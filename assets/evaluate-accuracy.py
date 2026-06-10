"""Evaluate model accuracy.

IMPORTANT: Weco optimizes a SINGLE metric. This script should print exactly one
metric in the format: metric_name: value (e.g., "accuracy: 0.95")

Constraint violations (latency limits, memory, etc.) should be printed as
regular messages - Weco will see them and avoid solutions that violate constraints.
"""
import importlib.util


def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


optimized = load_module(".weco/optimize.py")

# =============================================================================
# LOAD A REAL DATASET - Do NOT use hardcoded examples!
# =============================================================================
# When loading from URLs, prefer well-known versioned sources. Validate that
# downloaded data matches the expected format before processing.
#
# Use a real dataset appropriate for the task. Examples:
#
# Spam detection:
#   import pandas as pd
#   url = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
#   df = pd.read_csv(url, sep='\t', header=None, names=['label', 'text'])
#   X_test, y_test = df['text'].values, (df['label'] == 'spam').values
#
# General classification (sklearn):
#   from sklearn.datasets import fetch_20newsgroups, load_iris, load_digits
#   from sklearn.model_selection import train_test_split
#   data = fetch_20newsgroups(subset='test', categories=['sci.med', 'sci.space'])
#   X_test, y_test = data.data, data.target
#
# Hugging Face datasets:
#   from datasets import load_dataset
#   dataset = load_dataset("imdb", split="test[:1000]")
#   X_test, y_test = dataset["text"], dataset["label"]
#
# TODO: Replace with actual dataset loading for your task
X_test = None
y_test = None

# =============================================================================
# CONSTRAINT CHECKS (print violations, don't use as metrics)
# =============================================================================
# Example: Check inference latency constraint
# import time
# start = time.perf_counter()
# predictions = optimized.predict(X_test)
# latency_ms = (time.perf_counter() - start) * 1000
# max_latency_ms = 100  # Example constraint
# if latency_ms > max_latency_ms:
#     print(f"Constraint violated: latency {latency_ms:.1f}ms exceeds {max_latency_ms}ms limit")

# =============================================================================
# ACCURACY MEASUREMENT (the single metric to optimize)
# =============================================================================
# TODO: Replace with your prediction function
predictions = optimized.predict(X_test)
accuracy = (predictions == y_test).mean()

print(f"accuracy: {accuracy:.4f}")
