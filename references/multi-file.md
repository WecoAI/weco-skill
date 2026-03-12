---
name: multi-file
description: Optimizing code that spans multiple files
metadata:
  tags: multi-file, sources, dependencies, extraction
---

## Multi-File Optimization

Weco supports optimizing multiple files simultaneously using the `--sources` flag. This is the recommended approach when your optimization spans multiple files.

### Using `--sources`

Pass multiple files directly to Weco:

```bash
weco run --sources model.py utils.py config.py \
  --eval-command "bash .weco/evaluate.sh" \
  --metric accuracy \
  --goal maximize \
  --steps 10 \
  --output plain
```

Weco will optimize all specified files simultaneously, allowing changes across file boundaries.

### Limits

| Constraint | Limit |
|------------|-------|
| Max files | 10 |
| Max per file | 200 KB |
| Max total size | 500 KB |

If your files exceed these limits, use the extract-and-isolate fallback (see below).

### When to use `--sources`

Use `--sources` when:
- The hot path crosses file boundaries (e.g., a model file calls utility functions in another file)
- Changes in one file require coordinated changes in another
- You have 2-10 tightly coupled files within the size limits

### Choosing which files to include

Only include files that contain code Weco should modify. Do NOT include:
- Read-only config files or data files
- Large dependency files that won't change
- Test files (these belong in the evaluation script, not as optimization targets)

Trace the hot path from the user's target function through its imports. A file belongs in `--sources` only if it contains logic that needs to change for the optimization to succeed.

### Workspace setup with multiple files

When using isolated mode (`.weco/<task>/`):

```bash
mkdir -p .weco/<task>

# Copy all source files
cp path/to/model.py .weco/<task>/model.py
cp path/to/utils.py .weco/<task>/utils.py

# Keep baselines for comparison
cp path/to/model.py .weco/<task>/model.py.baseline
cp path/to/utils.py .weco/<task>/utils.py.baseline
```

Then run:

```bash
weco run --sources .weco/<task>/model.py .weco/<task>/utils.py \
  --eval-command "bash .weco/<task>/evaluate.sh" \
  --metric speedup \
  --goal maximize \
  --output plain
```

### Evaluation script for multi-file

The evaluation script doesn't change much — it just needs to load from the right paths:

```python
# .weco/<task>/evaluate.py
import importlib.util

def load_module(path, name="mod"):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# Load optimized modules
model = load_module(".weco/<task>/model.py", "model")
utils = load_module(".weco/<task>/utils.py", "utils")

# Evaluate
result = model.run(utils.preprocess(test_data))
print(f"accuracy: {result:.4f}")
```

---

## Fallback: Extract and Isolate

If `--sources` isn't suitable (e.g., too many files involved, or you only need to optimize a small function buried deep in a large codebase), extract the critical code into a single file.

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

### After Optimization: Reintegration

Once Weco finds an improvement:

1. Review the changes in the optimized file(s)
2. Understand what changed (don't blindly copy)
3. Port changes back to original file(s)
4. Run full test suite
5. Profile again to verify improvement in context
