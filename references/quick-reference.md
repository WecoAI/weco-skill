# Quick Reference

## Mode Comparison

| Aspect | Vibe Mode | Assistant Scientist Mode |
|--------|-----------|-------------------------|
| Questions asked | Minimal (just confirm before applying) | Conversational interview |
| Baseline | Dramatic presentation | Collaborative measurement |
| Optimization | Live progress updates | Detailed step-by-step with explanations |
| Explanation | Brief "why it won" | Deep educational dive |
| Impact | Tangible savings calculation | Full cost/benefit analysis |
| Best for | "Just make it faster" | Learning, complex cases |

## Key Rules

1. **Ask which mode** at the start of each optimization
2. **Present the baseline with context** - adapt framing based on current performance
3. **Celebrate wins** - tangible impact, not just percentages
4. **Explain why the winner won** - builds trust and teaches
5. **Always ask before modifying project files** - no exceptions
6. **Save a report** for every optimization (`.weco/<task>/report.md`)
7. The eval script MUST print exactly one line: `metric_name: value`

## Common Metrics

| Task | Metric | Goal |
|------|--------|------|
| Speed | `speedup` | maximize |
| Latency | `latency_ms` | minimize |
| Accuracy | `accuracy` | maximize |
| Loss | `loss` | minimize |
| F1 | `f1_score` | maximize |
| Memory | `peak_memory_mb` | minimize |
