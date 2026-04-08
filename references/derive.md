---
name: derive
description: Create derived runs to steer optimization in new directions
metadata:
  tags: derive, steer, branch, redirect, pivot
---

## What Are Derived Runs?

A **derived run** is a new optimization run whose baseline code comes from the best solution in the current lineage. All runs in a derivation chain share a **lineage** — a persistent record that tracks ancestry and the global best solution across every run.

Derive is the **primary steering mechanism** for Weco optimization. Instead of tweaking instructions mid-run or stopping and restarting from scratch, derive gives the optimizer a clean slate to explore a new direction from the best known solution — with full lineage tracking.

## When to Derive

- User says "try a different approach", "focus on X", "keep going"
- User adds constraints: "don't use Y", "only use Z"
- User wants to continue after a run completes: "try more steps", "explore further"
- User wants to branch: "try both approaches"

## How to Derive

Steering is passed via `-i / --additional-instructions` (inline text or path to a file). If omitted, the parent run's instructions are inherited unchanged.

```bash
# From the lineage-best step (global best across ALL runs in the lineage — default)
weco run derive <run-id> \
    --from-step best \
    -i "Focus on memory-efficient data structures" \
    --output plain

# From the best step in just the specified run
weco run derive <run-id> \
    --from-step run-best \
    -i "Try a completely different algorithm" \
    --output plain

# From a specific step number
weco run derive <run-id> \
    --from-step 7 \
    -i "Explore vectorization approaches" \
    --output plain

# With custom step count
weco run derive <run-id> \
    --from-step best \
    -i "Explore vectorization approaches" \
    --steps 50 \
    --output plain

# Inherit the parent's instructions unchanged (no -i)
weco run derive <run-id> --from-step best --output plain
```

### What Happens

1. The parent run is stopped automatically
2. A new run is created with the selected step's code as its **inherited baseline** (step 0)
3. Step 0 is inherited — no re-evaluation is performed, so no compute is wasted re-measuring a known-good solution
4. The first real candidate in the new run is step 1
5. The new run gets fresh LLM context (no accumulated history)
6. The optimization loop starts immediately
7. Both runs share the same objective (metric, goal, eval command) and the same lineage

### Options

| Option | Description |
|--------|-------------|
| `run_id` | Parent run UUID (required, positional) |
| `--from-step` | `best` (default: lineage-best = global best across ALL runs), `run-best` (best in the specified run only), or a step number |
| `-i, --additional-instructions` | Steering instructions for the new run (inline text or path to a file). If omitted, the parent run's instructions are inherited. |
| `-n, --steps` | Override step count (inherits from parent if omitted) |
| `--api-key` | API keys in `provider=key` format |
| `--output` | `rich` (interactive) or `plain` (machine-readable, use for automation) |

### Lineage Tracking

All derived runs share a **lineage**. Use `weco run status` to see lineage info:

```bash
weco run status <derived-run-id>
```

The response includes `lineage_id` and `derived_from` (the run, step, and node the new run was derived from).

To retrieve the full lineage (all runs, global best, ancestry):

```
GET /v1/lineages/{lineage_id}
```

## Agent Workflow

When a run completes, present the results and ask if the user would like to try a different approach. When the user gives a direction, derive immediately.

1. **Run completes** → present results, ask if they'd like to explore further
2. **User gives direction** → `weco run derive <run-id> --from-step best -i "..." --output plain` with `run_in_background: true`
3. **Monitor** → same monitoring loop as any other run

The user doesn't need to know about run IDs or lineage mechanics. From their perspective, you're just "trying a different approach." The run boundaries are an implementation detail.

### Example Conversations

**User asks to pivot:**
```
User: The speed gains are good but I care more about memory now.

Agent: [runs: weco run derive <id> --from-step best -i "Focus
       exclusively on reducing peak memory usage, even at the cost of
       some speed regression" --output plain]
```

**User adds constraints:**
```
User: Don't use PyTorch, only sklearn.

Agent: [runs: weco run derive <id> --from-step best -i "Do NOT
       use torch or transformers. Use sklearn only." --output plain]
```

**User wants to continue after completion:**
```
User: Try architectural changes instead of hyperparameter tuning.

Agent: [runs: weco run derive <id> --from-step best -i "Explore
       different model architectures — try attention mechanisms or
       residual connections" --output plain]
```
