---
name: multi-file
description: Optimizing across multiple files
metadata:
  tags: multi-file, scoping, dependencies
---

## Multi-File Optimization

Weco natively supports optimizing up to 10 files simultaneously. The optimizer sees all scoped files and can make coordinated changes across them while maintaining consistency.

### When to Use Multi-File Mode

Use `--sources` when the optimization requires changes across multiple files:
- Shared interfaces between modules
- Cross-file import dependencies
- Config + implementation that must stay in sync
- Model + utility code that needs joint optimization

```bash
weco run --sources src/model.py src/utils.py src/config.py \
  -c "python evaluate.py" -m latency -g minimize
```

### Limits

- **Maximum 10 files** per optimization run
- **200KB per file**, **500KB total** across all files
- Files are specified as paths relative to the project root
- Run the CLI from the project root directory

### When to Use Single-File Mode Instead

If the optimization target is a single hot path, single-file mode (`--source`) is simpler and uses fewer tokens:

```bash
weco run --source src/model.py -c "python evaluate.py" -m latency -g minimize
```

### Extracting Code for Large Codebases

If you have more than 10 files or exceed size limits, extract the relevant code:

#### Step 1: Identify the Hot Path

Profile first to find what actually needs optimization:

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
result = your_function(data)
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

#### Step 2: Scope Down to Key Files

Select only the files that contain the code paths being optimized. Leave config, tests, and infrastructure files out of the scoped set.

#### Step 3: Use Import Wrappers for Complex Dependencies

If dependencies outside the scoped files are too complex to inline:

```python
import sys
sys.path.insert(0, '/path/to/project')

from myproject.models import BaseModel
from myproject.utils import preprocess
```

### After Optimization

1. Review the changes across all modified files
2. Understand what changed and why
3. Run your full test suite
4. Profile again to verify improvement in context
