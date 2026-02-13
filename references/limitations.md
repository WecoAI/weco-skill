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

### Prompt Optimization (LLM-as-Judge)

When using LLM-as-judge to optimize prompts, skills, or natural language artifacts:

**Higher cost per evaluation**: Each evaluation requires LLM calls for both execution and judging. With 15 test scenarios, expect 30+ LLM calls per Weco step.

**Increased variance**: LLM outputs are non-deterministic, making metrics noisier than computational measurements. Mitigate with multiple runs per scenario and more test cases.

**Risk of gaming**: The prompt may optimize for judge preferences rather than real-world quality. Validate final results on held-out scenarios not used during optimization.

**Rubric sensitivity**: Small changes to the judge prompt can significantly affect scores. Lock the rubric before optimization and don't modify mid-run.

## Risk Mitigation

1. **Version control**: Commit before running Weco
2. **Comprehensive tests**: More tests = safer optimization
3. **Review changes**: Don't blindly accept suggestions
4. **Validate on held-out data**: Check for overfitting
5. **Profile after integration**: Verify improvement in full context
6. **Start small**: Use fewer steps first, increase if promising
