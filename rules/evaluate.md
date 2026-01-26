---
name: evaluate
description: Write evaluation scripts that measure metrics
metadata:
  tags: evaluate, metric, output, format
---

## Critical Requirement

The evaluation script MUST print the metric in this exact format:

```
metric_name: value
```

Examples:
```
speedup: 2.50
accuracy: 0.9523
loss: 0.0234
training_time: 45.7821
```

Weco parses this output to measure improvement.

## Constraint Violations

Print constraint violations as regular messages (not in metric format). Weco will see these and avoid solutions that violate constraints:

```python
if output != expected:
    print(f"Constraint violated: output differs from baseline")

if memory_mb > 4000:
    print(f"Constraint violated: memory usage {memory_mb}MB exceeds 4GB limit")
```

## Loading Modules

Use `importlib` to dynamically load the baseline and optimized modules:

```python
import importlib.util

def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

baseline = load_module(".weco/baseline.py")
optimized = load_module(".weco/optimize.py")
```

## Validating the Script

Before running optimization, validate that the evaluation script works:

```bash
bash .weco/evaluate.sh
```

Expected output for a baseline (comparing against itself):
- Speedup: `speedup: 1.0000` (no improvement yet)
- Accuracy: The actual accuracy value
- Loss: The actual loss value

## Templates

See the specific templates for each metric type:
- [eval-speed.md](eval-speed.md) - Performance/speedup
- [eval-accuracy.md](eval-accuracy.md) - Model accuracy
- [eval-loss.md](eval-loss.md) - Loss/error
- [eval-training-time.md](eval-training-time.md) - Training time
