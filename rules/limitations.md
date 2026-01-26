---
name: limitations
description: When NOT to use Weco and known limitations
metadata:
  tags: limitations, when-not-to-use, caveats, risks
---

## When NOT to Use Weco

### 1. When the Optimization is Trivial

Don't use Weco for obvious fixes:
- Adding `@functools.lru_cache`
- Vectorizing a simple loop with NumPy
- Using a more efficient data structure (dict instead of list search)

These take seconds to implement manually.

## Known Limitations

### Single File Only

Weco optimizes one file. For multi-file optimization:
- Extract the critical code to a single file
- Ensure dependencies are available
- Reintegrate changes manually after optimization

### No Multi-Objective Optimization

Weco optimizes ONE metric. You cannot directly optimize:
- Speed AND accuracy simultaneously
- Latency AND throughput trade-offs
- Model size AND performance

**Workaround**: Use constraints to bound other objectives:
```python
# Optimize accuracy, constrain latency
if latency_ms > 100:
    print("Constraint violated: latency exceeds 100ms")
print(f"accuracy: {accuracy:.4f}")
```

### No Guarantees

Weco may:
- Make code slower (if it explores bad directions)
- Introduce subtle bugs not caught by tests
- Find local optima, missing better solutions
- Use approaches you don't want (e.g., adding heavy dependencies)

### Cost

Each optimization step calls an LLM. 100 steps × evaluation time adds up.

### Stochasticity

Results vary between runs. The same optimization may find different solutions.

## Risk Mitigation

1. **Version control**: Commit before running Weco
2. **Comprehensive tests**: More tests = safer optimization
3. **Review changes**: Don't blindly accept suggestions
4. **Validate on held-out data**: Check for overfitting
5. **Profile after integration**: Verify improvement in full context
6. **Start small**: Use fewer steps first, increase if promising
