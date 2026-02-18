---
name: multi-file
description: Extracting optimizable code from larger codebases
metadata:
  tags: extraction, dependencies, isolation, refactoring
---

## The Single-File Constraint

Weco optimizes a single file. Real codebases have many files with complex dependencies.

## Strategy: Extract and Isolate

### Step 1: Identify the Hot Path

Profile first to find what actually needs optimization:

```python
# Using cProfile
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Run your code
result = your_function(data)
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions by time
```

### Step 2: Extract to a Self-Contained File

Create a single file that contains everything Weco needs:

```python
# .weco/optimize.py

# Option 1: Copy dependencies inline
# Instead of: from myproject.utils import helper
# Copy the helper function directly into this file

def helper(x):
    # Copied from myproject/utils.py
    return x * 2

def target_function(data):
    return helper(data)
```

### Step 3: Use Import Wrappers for Complex Dependencies

If dependencies are too complex to copy:

```python
# .weco/optimize.py
import sys
sys.path.insert(0, '/path/to/project')

# Now imports work
from myproject.models import BaseModel
from myproject.utils import preprocess

class OptimizedModel(BaseModel):
    def forward(self, x):
        # This is what Weco will optimize
        x = preprocess(x)
        return super().forward(x)
```

### Step 4: Handle Side Effects

Weco will modify the optimize.py file. Ensure side effects are contained:

```python
# BAD - side effects at import time
model = load_model()  # Runs when file is imported

# GOOD - lazy initialization
_model = None
def get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model
```

## Common Patterns

### Optimizing a Class Method

```python
# Original: myproject/model.py
class MyModel:
    def predict(self, x):
        # Complex logic
        pass

# .weco/optimize.py - extract just the method
import sys
sys.path.insert(0, '/path/to/project')
from myproject.model import MyModel

class OptimizedModel(MyModel):
    def predict(self, x):
        # Weco optimizes this
        # Start with copy of original implementation
        pass

# Export for evaluation
model = OptimizedModel()
def predict(x):
    return model.predict(x)
```

### Optimizing a Pipeline Stage

```python
# Original pipeline: load -> preprocess -> model -> postprocess

# .weco/optimize.py - just the slow stage
def preprocess(data):
    # Only this stage gets optimized
    # Other stages called from evaluation script
    pass
```

## Evaluation Script for Multi-File

```python
# .weco/evaluate.py
import sys
sys.path.insert(0, '/path/to/project')

# Load optimized module
import importlib.util
spec = importlib.util.spec_from_file_location("opt", ".weco/optimize.py")
optimized = importlib.util.module_from_spec(spec)
spec.loader.exec_module(optimized)

# Use project's data loading
from myproject.data import load_test_data
X_test, y_test = load_test_data()

# Evaluate
predictions = optimized.predict(X_test)
accuracy = (predictions == y_test).mean()
print(f"accuracy: {accuracy:.4f}")
```

## After Optimization: Reintegration

Once Weco finds an improvement:

1. Review the changes in `.weco/optimize.py`
2. Understand what changed (don't blindly copy)
3. Port changes back to original file(s)
4. Run full test suite
5. Profile again to verify improvement in context
