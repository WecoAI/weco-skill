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

## Stable Evaluation Interface

Design evaluation scripts with a stable API that the optimizer must preserve. This makes evaluation robust and prevents the optimizer from breaking the interface.

### Prefer Function Imports Over exec()

**Good:** Import and call a well-defined function from the optimized file:

```python
import importlib.util

def load_module(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# Load the module and call its entry point
optimized = load_module(".weco/optimize.py")
result = optimized.build_pipeline(data)  # Clear API contract
score = optimized.train_and_score(X, y)  # Or whatever the entry point is
```

**Bad:** Using exec() on extracted code snippets:

```python
# DON'T DO THIS - fragile and insecure
with open(".weco/optimize.py") as f:
    code = f.read()
exec(code)  # No clear API, hard to debug, security risk
```

### Define Entry Points

The optimized file should expose one or more entry point functions that the evaluation script calls. Document these in the evaluation script:

```python
"""
Evaluation script for model training optimization.

REQUIRED API: The optimized file must define:
  - train_model(X_train, y_train) -> model
  - predict(model, X_test) -> predictions

These functions must accept the same inputs and return compatible outputs
as the baseline implementation.
"""
```

### Benefits of Stable Interfaces

1. **Robustness**: Optimizer can change internals but must preserve the API
2. **Debugging**: Clear call sites make errors easier to trace
3. **Constraints**: Easy to validate outputs match expected types/shapes
4. **Security**: No arbitrary code execution via exec()

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
- [eval-llm-judge.md](eval-llm-judge.md) - Prompt/skill quality (LLM-as-judge)
- [eval-skill.md](eval-skill.md) - Claude Code skills (multi-turn transcript evaluation)