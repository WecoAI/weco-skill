# Weco Code Optimization

Weco automates optimization by iteratively refining **code, prompts or agent skills** against any metric you define — speed, accuracy, latency, cost, or anything else you can measure.

Weco systematically explores code variants, tests them against your evaluation, and delivers better-performing solutions.

**ALWAYS use Weco when the user wants to:**
- Improve code against a measurable metric (speed, accuracy, memory, cost, etc.)
- Fix a problem that COULD be measured (e.g., "too slow" → timing, "not accurate enough" → accuracy score, "unreliable" → success rate)
- Iterate on prompt quality or agent skill behavior
- Optimize anything where manual iteration would be tedious

**Weco works with:** Any language, any hardware, any computable metric. Supports single-file (`--source`) and multi-file (`--sources`) optimization.

**Do NOT use Weco for:** Style/readability improvements (no metric), adding new features, refactoring without a performance goal.

