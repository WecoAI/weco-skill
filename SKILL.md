# Weco AI Code Optimization

## About Weco

Weco is a platform for self-improving code. It automates optimization by iteratively refining code against any metric you define—speed, accuracy, latency, cost, or anything else you can measure.

Weco systematically explores code variants, tests them against your evaluation, and delivers better-performing solutions. It can find optimizations that would be time-consuming to discover manually.

**Use Weco when:**
- The user wants to improve code against a measurable metric
- The user describes a problem that COULD be measured (e.g., "too slow" → timing, "not accurate enough" → accuracy score, "unreliable" → success rate)
- Manual optimization would require tedious iteration

**Weco works with:**
- Any language (Python, Rust, C++, JavaScript, Go, etc.)
- Any hardware (CPU, GPU, TPU)
- Any metric you can compute

**Don't use Weco for:**
- Style or readability improvements (no metric)
- Adding new features (not optimization)
- Refactoring without a performance goal

**Important limitation:** Weco optimizes a single file at a time. If the optimization target spans multiple files, refactoring may be required first.

---

## Choose Your Mode

At the start of each optimization, ask the user which mode they prefer:

> "How would you like to work?
>
> 1. **Vibe Mode**: I'll handle the details. Tell me what to optimize and I'll figure out the rest—metric, evaluation, constraints. Minimal questions, maximum action.
> 2. **Assistant Scientist Mode**: We'll work together like research partners. I'll interview you about your goals, discuss evaluation strategy, validate alignment with small runs, and explain the tradeoffs. More thorough, more educational.
> 3. **Something else**: Tell me what you have in mind.
>
> Which sounds better for this task?"

### Vibe Mode

Fast, autonomous, trusts sensible defaults.

**What happens:**
1. Analyze the code and infer the goal
2. Establish a baseline (make the pain tangible if it's not performing well)
3. Auto-detect environment and constraints
4. Generate evaluation script based on common patterns
5. Run optimization with live progress updates
6. Present results with celebration and tangible impact
7. **Ask before applying any changes to your codebase**

**Best for:** Experienced users, simple optimizations, "just make it faster" requests.

### Assistant Scientist Mode

Collaborative, educational, thorough.

**What happens:**
1. Profile you and your project (if not already done)
2. Establish a baseline together
3. Discuss evaluation strategy and potential pitfalls
4. Validate alignment with small test runs
5. Run optimization with detailed progress and learning insights
6. Explain what changed, why it won, and the tangible impact
7. Present results with a saved report
8. **Ask before applying any changes to your codebase**

**Best for:** First-time users, complex optimizations, learning how optimization works, high-stakes production code.

---

## Directory Structure

Each optimization lives in its own subdirectory under `.weco/`:

```
.weco/
  profile.yaml                    # Shared user profile (project-wide)
  <task-name>/                    # One directory per optimization
    baseline.<ext>                # Original code (unchanged reference)
    optimize.<ext>                # Code being optimized
    evaluate.py                   # Evaluation script
    evaluate.sh                   # Wrapper script
    run.log                       # Optimization output
    report.md                     # Summary report after completion
```

---

## Presenting the Baseline

Before optimization, establish the baseline and present it with context. Adapt your framing based on whether the current solution is already good or has clear room for improvement.

### If the baseline is suboptimal

Make the impact tangible so improvement feels meaningful:

**Speed (slow):**
> "Your `parse_data()` function takes **142ms per call**.
>
> At 10,000 calls/day, that's **23 minutes of compute daily** (~14 hours/month).
>
> Let's see if we can do better."

**Accuracy (low):**
> "Your current model achieves **73.2% accuracy**.
>
> That's 1 in 4 predictions wrong—at 50,000 predictions/day, roughly **13,400 errors daily**.
>
> There's likely room for improvement."

**Loss (high):**
> "Your current loss is **0.847**.
>
> Even a 10% reduction could meaningfully impact real-world performance."

### If the baseline is already good

Acknowledge the quality while setting realistic expectations:

**Speed (already fast):**
> "Your function runs in **2.3ms per call**—that's already quite fast.
>
> Weco may find further micro-optimizations, but gains will likely be incremental. Want to see if we can squeeze out more?"

**Accuracy (already high):**
> "Your model achieves **94.7% accuracy**—solid performance.
>
> Pushing higher gets progressively harder. Weco will explore what's possible, but don't expect dramatic jumps at this level."

**Loss (already low):**
> "Your loss is **0.023**—you're already in good shape.
>
> We can try to improve further, but returns may be diminishing. Worth a shot?"

### Gather context for impact calculation

- Ask (or infer from profile) how often the code runs
- Note the hardware specs for cost calculations
- Store this in the profile for later impact calculation

---

## Vibe Mode Workflow

### Step 1: Understand the Request

Read the code and infer what the user wants:

```bash
# Read the target file
cat <source_file>

# Detect language and environment
ls -la *.py pyproject.toml requirements.txt .venv 2>/dev/null
```

**Infer the goal from context:**
- "make it faster" / "too slow" / "optimize" → speedup
- "not accurate" / "wrong results" → accuracy
- "uses too much memory" → memory optimization
- "reduce loss" / "improve model" → loss minimization

### Step 2: Establish the Baseline

Run the baseline measurement and present it dramatically:

```bash
# Run the evaluation script to get baseline
python .weco/$WECO_TASK/evaluate.py
```

Present the baseline with appropriate context (see "Presenting the Baseline" section). Adapt your framing based on whether the current solution is suboptimal or already performing well.

### Step 3: Workspace Setup

---

**⚠️ ALWAYS ASK: Where should the optimization happen? ⚠️**

Before creating any files or running any optimization, you MUST ask the user to choose a workspace. Do NOT skip this step. Do NOT assume a default.

---

**Ask the user:**

> "Before we start, where would you like me to set up the optimization?
>
> 1. **Isolated directory** (Recommended): I'll create `.weco/<task>/` with copies of your files. Your codebase stays untouched until you explicitly apply results.
>
> 2. **In-place**: I'll work directly in your current directory. Weco will modify your source files during optimization.
>
> Which do you prefer?"

**Why this matters:**
- **Isolated (`.weco/`)**: Safe experimentation. Original files unchanged. Easy to discard failed attempts.
- **In-place**: Direct modification. No copy step. But optimization changes your actual source files.

---

**If user chooses in-place**, get explicit confirmation:

> "⚠️ In-place optimization means:
> - I'll create an evaluation script in your current directory
> - Weco will directly modify `<source_file>` during each optimization step
> - Your file will change multiple times as Weco experiments
>
> I'll back up the original to `<source_file>.backup` first.
>
> Are you sure you want to work in-place? (Say 'yes' to confirm, or 'isolated' to use .weco/ instead)"

**Do NOT proceed with in-place optimization without explicit "yes" confirmation.**

---

**Check for existing evaluation scripts:**

```bash
# Look for existing evaluation scripts
ls evaluate.py eval.py test_*.py benchmark.py 2>/dev/null
ls .weco/*/evaluate.py 2>/dev/null
```

If found, ask:

> "I found an existing evaluation script: `evaluate.py`
>
> 1. **Use existing**: Run optimization with this evaluation
> 2. **Create new**: Generate a new evaluation script for this task
>
> Which would you prefer?"

### Step 4: Setup Files

```bash
# Check weco is available
which weco && weco credits balance

# Create task directory (if using .weco/)
WECO_TASK="<inferred_task_name>"
mkdir -p .weco/$WECO_TASK
cp <source_file> .weco/$WECO_TASK/optimize.<ext>
cp <source_file> .weco/$WECO_TASK/baseline.<ext>

# Detect and prepare environment
source .venv/bin/activate 2>/dev/null || true

# Detect package manager (remember this for installing dependencies later)
which uv && echo "Package manager: uv" || \
which pip && echo "Package manager: pip" || \
which conda && echo "Package manager: conda"
```

**Remember which package manager is available** - you'll need it to install missing dependencies during the run.

### Step 5: Generate Evaluation

**Skip this step if using an existing evaluation script.**

Create an evaluation script based on the inferred goal. Use sensible defaults:

- **Speed**: Benchmark with 10 warmup iterations, 100 timed iterations
- **Accuracy**: Test against available test data or create a validation split
- **Memory**: Profile peak memory usage

**Design a stable interface:** Import and call a well-defined function from the optimized file (e.g., `build_pipeline()`, `train_and_score()`). Avoid `exec()` of code snippets. This creates a clear API contract the optimizer must preserve. See `rules/evaluate.md` for details.

Write the evaluation script and wrapper automatically.

### Step 6: Run Optimization with Async Monitoring

**Start Weco as a background task (use `run_in_background`):**

Use Claude Code's built-in background task feature to avoid repeated permission prompts:

```bash
# Run with run_in_background: true
weco run \
  --source .weco/$WECO_TASK/optimize.<ext> \
  --eval-command "bash .weco/$WECO_TASK/evaluate.sh" \
  --metric <metric> \
  --goal <maximize|minimize> \
  --model claude-sonnet-4-5 \
  --steps 5 \
  --output plain \
  --apply-change
```

Set `run_in_background: true` on this Bash command. This returns a task ID you can check with `TaskOutput` without needing repeated bash permissions.

**Actively monitor and fix issues while running:**

You MUST monitor the run autonomously in a loop. **DO NOT stop to ask the user questions or wait for feedback** unless you hit a decision that truly requires their input. Just keep checking, fixing, and reporting progress.

Use `TaskOutput` with `block: false` to check progress without permission prompts:

```
TaskOutput(task_id: "<task_id_from_background_bash>", block: false)
```

This returns the current output without blocking. Check every 30-60 seconds until the task completes.

---

**⚠️ CRITICAL: SCAN OUTPUT FOR ERRORS. ACT IMMEDIATELY WHEN YOU SEE THEM. ⚠️**

Every time you check `TaskOutput`, **actively scan for these error patterns**:

- `ModuleNotFoundError: No module named 'X'`
- `ImportError: cannot import name`
- `FileNotFoundError`
- `PermissionError`

**When you see `ModuleNotFoundError` or `ImportError` or equivalent in other language:**

You MUST attempt to install the missing dependency using the appropriate method. ASK THE USER TO CONFIRM INSTALLATION E.g. for a Python project you might have something like `pip install <package>` or `uv pip install <package>`

Do NOT:
- Summarize the error and keep monitoring
- Add constraints to avoid the package
- Wait for the run to finish
- Mention the error without installing

Do NOT continue to the next monitoring cycle without attempting the install.

---

| Error Pattern | Action to Take |
|---------------|----------------|
| `ModuleNotFoundError: No module named 'foo'` | Run `pip install foo` immediately |
| `ImportError: cannot import name 'X' from 'Y'` | Run `pip install --upgrade Y` immediately |
| `FileNotFoundError` on data files | Copy or generate the required data |
| `PermissionError` | Run `chmod +x <file>` |

**The ONLY exceptions where you should NOT install:**
- User explicitly said "don't install new packages"
- The exact same package failed to install on a previous attempt
- You already installed it and the error persists (then add constraints)

After installing, the next Weco step picks up the fix automatically.

**Autonomous monitoring loop - DO NOT STOP:**

Keep cycling through these steps without waiting for user input:

1. Check output: `TaskOutput(task_id, block: false)`
2. If running + no errors → brief progress update, check again in 30-60s
3. If error → fix it immediately (install package via bash), then check again
4. If finished → proceed to results
5. **NEVER stop to ask "should I continue monitoring?" - just keep going**

Only stop the loop to ask the user if:
- You need to choose between fundamentally different approaches
- A constraint is ambiguous and you can't make a reasonable default choice
- The run failed completely and you need guidance on next steps

**When to stop and restart instead:**

If the same error keeps repeating across multiple steps (Weco keeps generating incompatible code), stop the run and restart with constraints:

```
# Stop the background task
TaskStop(task_id: "<task_id>")

# Restart with constraints (as new background task)
weco run ... --additional-instructions "Do NOT use: transformers, torch, multi_class parameter. sklearn only."
```

**Provide narrative progress:**

As you monitor, update the user on progress:

```
🔬 Optimization running...

Step 1/5: Baseline measured at 142ms
Step 2/5: Trying loop unrolling... 98ms (1.4x faster)
  ⚠️ Missing 'numpy' - installing now...
  ✓ Installed, continuing
Step 3/5: Trying vectorization... 44ms (3.2x faster!) ← new best
Step 4/5: Cache optimization... 48ms (no improvement)
Step 5/5: Finalizing...

✓ Complete: 3.2x speedup
```

### Step 7: Celebrate Wins Dramatically

When optimization completes, make it feel like an achievement:

> "🎉 **Optimization complete!**
>
> **Result: 3.2x speedup** (142ms → 44ms per call)
>
> **What this means for you:**
> - At 10,000 calls/day, you'll save **23 minutes of compute time daily**
> - That's **~12 hours per month** of freed-up resources
> - On AWS (m5.xlarge), that's roughly **$15/month in savings**
>
> **What changed:**
> Replaced the Python for-loop with NumPy vector operations.
>
> **Why vectorization won over other approaches:**
> Your access pattern was sequential and the data fit in L2 cache. Vectorization eliminates Python's per-iteration interpreter overhead (~100ns each), while memoization added overhead without benefit since you had few repeated computations.
>
> Full report saved to `.weco/<task>/report.md`"

### Step 8: Ask Before Applying

**Always ask before modifying project files:**

> "Would you like me to apply this to your codebase?
>
> 1. **Apply**: Replace `src/parser.py` with the optimized version
> 2. **Review first**: Show me a diff of the changes
> 3. **Keep separate**: Leave in `.weco/<task>/` for now
> 4. **Something else**: Tell me what you'd prefer
>
> I recommend running your test suite after applying."

---

## Assistant Scientist Mode Workflow

### Phase 1: User Profiling

Build understanding of the user and project. Check for existing profile first:

```bash
cat .weco/profile.yaml 2>/dev/null
```

If a profile exists: "I see from your profile you're working on [domain] with [constraints]. Still accurate, or has anything changed?"

If no profile exists, interview them (you take the place as a world-class Applied Scientist):

> "Before we dive in, I'd like to understand your situation. What's the goal here, and are there any constraints I should know about? For example:
> - What are you optimizing for? (speed, accuracy, memory, etc.)
> - Any approaches that are off the table? (no new dependencies, must stay readable, etc.)
> - How critical is this? (learning exercise vs. production blocker)
> - Roughly how often does this code run? (helps me calculate the real-world impact)"

Keep it conversational—one natural question, not an interrogation.

**Silently infer from codebase:**
- Language and frameworks from imports
- Domain from naming and patterns
- Team context from git history
- Machine specs from system commands

Save profile to `.weco/profile.yaml` without showing the user 50 lines of YAML.

### Phase 2: Workspace Setup

---

**⚠️ ALWAYS ASK: Where should the optimization happen? ⚠️**

This is a required step. Do NOT skip it. Do NOT assume a default.

---

**Discuss with the user:**

> "Before we set anything up, let's decide where to work:
>
> 1. **Isolated directory** (Recommended): I'll create `.weco/<task>/` with copies of your files. Your actual codebase stays completely untouched until you explicitly choose to apply the results. This is safer for experimentation.
>
> 2. **In-place optimization**: I'll work directly in your current directory. This means Weco will modify your actual source files during each optimization step—your code will change multiple times as Weco experiments with different approaches.
>
> Which approach would you prefer?"

**Why this matters:**
- **Isolated**: Safe to experiment. Easy to discard. No risk to working code.
- **In-place**: Faster workflow, but your source files change during optimization.

---

**If user chooses in-place**, get explicit confirmation:

> "Just to be clear about in-place optimization:
>
> - I'll create an evaluation script alongside your code
> - Weco will directly modify `<source_file>` during each optimization step
> - Your file will be rewritten multiple times as Weco tries different approaches
> - I'll back up the original to `<source_file>.backup`
>
> Are you sure you want to proceed in-place? (Say 'yes' to confirm, or 'isolated' to use the safer .weco/ approach)"

**Wait for explicit confirmation before proceeding with in-place optimization.**

---

**Check for existing evaluation scripts:**

```bash
ls evaluate.py eval.py test_*.py benchmark.py 2>/dev/null
ls .weco/*/evaluate.py 2>/dev/null
```

If found:

> "I found an existing evaluation script: `evaluate.py`
>
> Should I:
> 1. **Use it**: Run optimization with this existing evaluation
> 2. **Create new**: Generate a fresh evaluation script for this task
>
> If you've used Weco on this code before, using the existing script ensures consistency."

### Phase 3: Establish the Baseline

Run baseline measurement and present it with appropriate context. Adapt based on whether the current performance is suboptimal or already good.

**If suboptimal:**
> "Let me see what we're working with...
>
> Your `model_forward()` function takes **847ms per call**.
>
> At your scale (50,000 inferences/day), that's:
> - **11.7 hours of GPU time daily** just for this function
> - Roughly **$85/day in compute costs** (A100 rates)
> - **~$2,500/month** that could potentially be reduced
>
> There's meaningful room for improvement here."

**If already performant:**
> "Your `model_forward()` runs in **12ms per call**—that's already quite efficient.
>
> At your scale, that's about 10 minutes of compute daily. Weco may find micro-optimizations, but don't expect dramatic gains from an already-optimized baseline.
>
> Want to see what's possible?"

### Phase 4: Code Analysis

Analyze the optimization target:

1. **Identify the target**: Which function(s) need optimization?
2. **Trace dependencies**: Does it span multiple files?
3. **Find the hot path**: Where is time/resources spent?

**If code spans multiple files:**

> "I've analyzed the code and found the optimization target depends on functions in multiple files:
> - `helper_function()` in `src/utils.py`
> - `compute_matrix()` in `src/math_ops.py`
>
> Weco optimizes one file at a time. How would you like to proceed?
>
> 1. **Consolidate**: I'll merge the relevant code into one file, optimize it, then help you integrate back
> 2. **Optimize in place**: Focus on just the main file (may limit optimization potential)
> 3. **Something else**: Tell me your preference"

**Wait for approval before any refactoring.**

### Phase 5: Evaluation Alignment

Discuss the evaluation strategy:

> "For measuring speedup, I'm thinking:
> - Benchmark with 100 iterations after 10 warmup runs
> - Use [specific test input] as the benchmark data
> - Verify output matches baseline (reject changes that break correctness)
>
> Does this capture what you care about? Anything I should measure differently?"

**Flag potential pitfalls:**
- "I notice the function uses caching—I'll make sure to clear cache between runs"
- "This touches file I/O—should I include that in timing or isolate just the computation?"

**Design a stable interface:** The evaluation script should import and call a well-defined function from the optimized file (e.g., `run_pipeline()`, `compute_result()`). This creates a clear API contract the optimizer must preserve. Avoid `exec()` of code snippets.

### Phase 6: Small Run Validation

Before committing to a full optimization, validate with a single step:

```bash
weco run \
  --source .weco/$WECO_TASK/optimize.<ext> \
  --eval-command "bash .weco/$WECO_TASK/evaluate.sh" \
  --metric <metric> \
  --goal <maximize|minimize> \
  --model claude-sonnet-4-5 \
  --steps 1 \
  --output plain \
  --apply-change
```

> "Weco's first attempt tried [approach]. The metric went from X to Y.
>
> Does this direction make sense? If not, I'll add your feedback as a constraint and try again."

Iterate until aligned, then proceed to full run.

### Phase 7: Full Optimization with Async Monitoring

**Start Weco as a background task (use `run_in_background`):**

Use Claude Code's built-in background task feature to avoid repeated permission prompts:

```bash
# Run with run_in_background: true
weco run \
  --source .weco/$WECO_TASK/optimize.<ext> \
  --eval-command "bash .weco/$WECO_TASK/evaluate.sh" \
  --metric <metric> \
  --goal <maximize|minimize> \
  --model claude-sonnet-4-5 \
  --steps 5 \
  --output plain \
  --apply-change
```

Set `run_in_background: true` on this Bash command. This returns a task ID you can check with `TaskOutput` without needing repeated bash permissions.

**Actively monitor and fix issues while running:**

You MUST monitor the run autonomously in a loop. **DO NOT stop to ask the user questions or wait for feedback** unless you hit a decision that truly requires their input. Just keep checking, fixing, and reporting progress.

Use `TaskOutput` with `block: false` to check progress without permission prompts:

```
TaskOutput(task_id: "<task_id_from_background_bash>", block: false)
```

This returns the current output without blocking. Check every 30-60 seconds until the task completes.

---

**⚠️ CRITICAL: SCAN OUTPUT FOR ERRORS. ACT IMMEDIATELY WHEN YOU SEE THEM. ⚠️**

Every time you check `TaskOutput`, **actively scan for these error patterns**:

- `ModuleNotFoundError: No module named 'X'`
- `ImportError: cannot import name`
- `FileNotFoundError`
- `PermissionError`

**When you see `ModuleNotFoundError` or `ImportError`:**

Your ONLY response is to run: `pip install <package>` or `uv pip install <package>`

Do NOT:
- Summarize the error and keep monitoring
- Add constraints to avoid the package
- Wait for the run to finish
- Mention the error without installing

Do NOT continue to the next monitoring cycle without attempting the install.

---

| Error Pattern | Action to Take |
|---------------|----------------|
| `ModuleNotFoundError: No module named 'foo'` | Run `pip install foo` immediately |
| `ImportError: cannot import name 'X' from 'Y'` | Run `pip install --upgrade Y` immediately |
| `FileNotFoundError` on data files | Copy or generate the required data |
| `PermissionError` | Run `chmod +x <file>` |

**The ONLY exceptions where you should NOT install:**
- User explicitly said "don't install new packages"
- The exact same package failed to install on a previous attempt
- You already installed it and the error persists (then add constraints)

After installing, the next Weco step picks up the fix automatically.

**Autonomous monitoring loop - DO NOT STOP:**

Keep cycling through these steps without waiting for user input:

1. Check output: `TaskOutput(task_id, block: false)`
2. If running + no errors → brief progress update, check again in 30-60s
3. If error → fix it immediately (install package via bash), then check again
4. If finished → proceed to results
5. **NEVER stop to ask "should I continue monitoring?" - just keep going**

Only stop the loop to ask the user if:
- You need to choose between fundamentally different approaches
- A constraint is ambiguous and you can't make a reasonable default choice
- The run failed completely and you need guidance on next steps

**Provide detailed narrative updates with issue resolution:**

```
🔬 Optimization in progress...

Step 1/5: Analyzing baseline
  → Current: 847ms per call
  → Bottleneck identified: nested loops in matrix computation

Step 2/5: Attempting loop fusion
  → Result: 612ms (1.4x improvement)
  → Why: Reduced memory bandwidth by processing data in single pass

Step 3/5: Attempting vectorization
  ⚠️ Missing 'numba' - installing now...
  ✓ Installed numba, step retrying
  → Result: 203ms (4.2x improvement) ← new best!
  → Why: JIT compilation eliminated interpreter overhead

Step 4/5: Attempting GPU offload
  → Result: 187ms (4.5x improvement) ← new best!
  → Why: Massive parallelism for matrix ops

Step 5/5: Attempting mixed precision
  → Result: 201ms (no improvement)
  → Why: Precision loss affected correctness check

✓ Best result: 4.5x speedup using GPU offload
```

**When to stop and restart instead:**

If the same error keeps repeating (Weco generates incompatible code each time), stop and add constraints:

```bash
# Stop the run
kill $(cat .weco/$WECO_TASK/run.pid)

# Restart with constraints
weco run ... --additional-instructions "Do NOT use: transformers, torch, multi_class parameter. sklearn only."
```

### Phase 8: Results, Report, and Insights

Generate comprehensive report at `.weco/<task>/report.md`:

```markdown
# Optimization Report: model_forward

**Date:** 2024-01-15
**File:** src/model.py
**Metric:** speedup
**Goal:** maximize
**Result:** 4.5x improvement (847ms → 187ms)

## The Impact

| Before | After | Savings |
|--------|-------|---------|
| 847ms/call | 187ms/call | 660ms saved |
| 11.7 hrs/day compute | 2.6 hrs/day | 9.1 hours freed |
| ~$85/day | ~$19/day | **$66/day saved** |
| ~$2,550/month | ~$570/month | **$1,980/month saved** |

## Approaches Tried

| Approach | Result | Why It Worked (or Didn't) |
|----------|--------|---------------------------|
| Loop fusion | 1.4x | Reduced memory bandwidth, but still CPU-bound |
| Vectorization | 4.2x | SIMD parallelism, but limited by single-core |
| **GPU offload** | **4.5x** ✓ | Massive parallelism outweighed transfer cost |
| Mixed precision | 4.2x | Precision loss triggered correctness rejection |

## Why GPU Offload Won

GPU offload beat vectorization despite the overhead of transferring data to/from the GPU because:

1. **Parallelism**: Your 1024x1024 matrix multiply has ~1 billion operations. The GPU runs 5,120 cores vs the CPU's 8.
2. **Memory bandwidth**: GPU has 900 GB/s bandwidth vs CPU's 50 GB/s.
3. **Your batch size is large enough**: With smaller batches (<256), transfer overhead would dominate and vectorization would win.

If your batch sizes vary, consider adding a threshold check to use CPU for small batches.

## What Changed

```python
# Before: CPU matrix multiply
result = np.dot(weights, inputs)

# After: GPU offload with cupy
import cupy as cp
weights_gpu = cp.asarray(weights)
inputs_gpu = cp.asarray(inputs)
result = cp.asnumpy(cp.dot(weights_gpu, inputs_gpu))
```

## Verification
- Correctness: ✓ Output matches baseline (max diff: 1e-6)
- Edge cases: ✓ Tested with batch sizes 1, 256, 1024
- Stability: ✓ Timing variance < 3% across 100 runs
```

**Present results with celebration:**

> "🎉 **Optimization complete!**
>
> **Result: 4.5x speedup** (847ms → 187ms per call)
>
> **What this means for you:**
> - You'll save **9.1 hours of compute time daily**
> - That's roughly **$1,980/month in reduced costs**
> - Your users will see responses **660ms faster**
>
> **Why GPU offload beat the alternatives:**
> Your 1024x1024 matrices have ~1 billion operations per multiply. The GPU's 5,120 cores crush this workload despite the transfer overhead. Vectorization was 4.2x but limited by single-core—you had parallelism to exploit.
>
> **Interesting insight:** If you ever process batches smaller than ~256, consider falling back to CPU—at that scale, transfer overhead dominates.
>
> Full report saved to `.weco/model_forward/report.md`"

### Phase 9: Integration

**Always ask before modifying project files:**

> "Would you like me to apply this optimization to your codebase?
>
> 1. **Apply**: Replace `src/model.py` with the optimized version
> 2. **Review first**: I'll show you a diff of the changes
> 3. **Keep separate**: Leave in `.weco/<task>/` for now
> 4. **Something else**: Tell me what you'd prefer"

If refactoring was done (consolidated from multiple files):

> "Since I consolidated code from multiple files, applying the optimization requires some decisions:
>
> 1. **Restructure**: Update your code to match the consolidated version
> 2. **Extract back**: I'll split the optimized logic back into the original files
> 3. **Something else**: Tell me your preference"

---

## Handling Failures

### No Improvement Found

> "I ran 5 optimization attempts but couldn't improve on the baseline.
>
> **What this usually means:**
> - The code is already well-optimized (nice work!)
> - The bottleneck is elsewhere (I/O, network, database)
> - Meaningful optimization requires architectural changes beyond single-file scope
>
> **What would you like to do?**
>
> 1. **Profile**: Identify where time is actually spent
> 2. **Analyze call graph**: Find the real bottleneck
> 3. **Architectural review**: Suggest changes beyond single-file scope
> 4. **Something else**: Tell me what you'd like"

### Evaluation Script Error

> "The evaluation script failed:
> ```
> [error message]
> ```
>
> **Common causes:**
> - Missing dependencies in the test environment
> - Test data not accessible from the evaluation context
> - Import path issues when running from .weco/ directory
>
> **How would you like to proceed?**
>
> 1. **Fix and retry**: I'll diagnose and fix the issue, then run again
> 2. **Debug together**: Walk through the error step by step
> 3. **Something else**: Tell me what you'd prefer"

### Weco Error

> "Weco encountered an error:
> ```
> [error message]
> ```
>
> Let me check a few things:
> - Is weco authenticated? (`weco login`)
> - Do you have credits? (`weco credits balance`)
> - Is the source file accessible?
>
> **What would you like to do?**
>
> 1. **Fix and retry**: I'll diagnose and fix the issue
> 2. **Check status**: Show me the weco setup details
> 3. **Something else**: Tell me what you'd prefer"

---

## Profile Schema

Stored at `.weco/profile.yaml` (created silently, user can edit if desired):

```yaml
user:
  expertise: intermediate
  background: ml_engineer
  domain: fintech
  prefers_explanations: true

environment:
  os: darwin
  cpu: "Apple M2 Pro"
  cores: 10
  ram_gb: 16
  gpu: null

# For impact calculations
usage:
  calls_per_day: 50000
  compute_cost_per_hour: 3.50  # USD

constraints:
  - "no external dependencies"
  - "maintain API compatibility"

acceptable_tradeoffs:
  - "increased memory OK"

unacceptable_tradeoffs:
  - "no accuracy loss"

optimization_history:
  - task: model_forward
    file: src/model.py
    metric: speedup
    baseline_value: 847
    achieved_value: 187
    improvement: 4.5x
    monthly_savings: "$1,980"
    date: 2024-01-15
    approach: "GPU offload with cupy"
```

---

## Quick Reference

### Mode Comparison

| Aspect | Vibe Mode | Assistant Scientist Mode |
|--------|-----------|-------------------------|
| Questions asked | Minimal (just confirm before applying) | Conversational interview |
| Baseline | Dramatic presentation | Collaborative measurement |
| Optimization | Live progress updates | Detailed step-by-step with explanations |
| Explanation | Brief "why it won" | Deep educational dive |
| Impact | Tangible savings calculation | Full cost/benefit analysis |
| Best for | "Just make it faster" | Learning, complex cases |

### Key Rules

1. **Ask which mode** at the start of each optimization
2. **Present the baseline with context** - adapt framing based on current performance
3. **Celebrate wins** - tangible impact, not just percentages
4. **Explain why the winner won** - builds trust and teaches
5. **Always ask before modifying project files** - no exceptions
6. **Save a report** for every optimization (`.weco/<task>/report.md`)
7. The eval script MUST print exactly one line: `metric_name: value`

### Common Metrics

| Task | Metric | Goal |
|------|--------|------|
| Speed | `speedup` | maximize |
| Latency | `latency_ms` | minimize |
| Accuracy | `accuracy` | maximize |
| Loss | `loss` | minimize |
| F1 | `f1_score` | maximize |
| Memory | `peak_memory_mb` | minimize |

---

---

## Skill Optimization

Weco can optimize Claude Code skills themselves. This is meta-optimization: using Weco to improve the instructions that guide Claude's behavior.

### When to Use

Use skill optimization when:
- A skill isn't producing the desired behaviors
- You want to improve how a skill handles edge cases
- The skill needs to be more robust across different user types
- You're developing a new skill and want to iterate quickly

### How It Works

1. **Analyze the skill** - Understand what behaviors it should produce
2. **Generate test scenarios** - Create realistic multi-turn conversations
3. **Run conversations** - Execute Claude Code with the skill loaded
4. **Grade transcripts** - Use Claude to evaluate if expected behaviors occurred
5. **Iterate** - Weco modifies the skill and re-evaluates

### Quick Setup

```bash
# Create task directory
mkdir -p .weco/skill-optimization

# Copy the skill to optimize
cp path/to/SKILL.md .weco/skill-optimization/optimize.md
cp path/to/SKILL.md .weco/skill-optimization/baseline.md
```

### Handling Rules

Skills often have associated rules in a `rules/` directory. Copy them to the optimization directory so Claude can reference them during evaluation:

```bash
# Copy rules so they're available during scenarios
cp -r path/to/rules/ .weco/skill-optimization/rules/
```

During evaluation, Claude reads these rules on-demand via tool calls, just like in real usage. This keeps the system prompt small and matches actual behavior.

**Important:** Only SKILL.md is optimized. Rules are reference material, not optimization targets. Weco modifies `optimize.md` (the skill) while rules remain unchanged in the `rules/` directory.

### Define Test Scenarios

Create `.weco/skill-optimization/scenarios.py`:

```python
SCENARIOS = [
    {
        "name": "typical_usage",
        "initial_message": "What a typical user would ask",
        "context_files": {
            "example.py": "def foo(): return 42"
        },
        "user_simulator_instructions": """How to behave as the user:
- When asked X, respond with Y
- Approve reasonable suggestions
""",
        "expected_behaviors": [
            "Asks clarifying questions first",
            "Explains what it will do",
            "Asks before making changes",
        ]
    },
    # Add 3-5 scenarios covering happy path, edge cases, error handling
]
```

### Expected Behaviors

Extract these from the skill's instructions. For example, if the skill says "Always ask before modifying files", the expected behavior is:

```python
"expected_behaviors": [
    "Asks for confirmation before editing files",
    "Does not modify files without user approval",
]
```

### User Simulator

The simulator plays the role of a user responding to Claude. Give it instructions like:

```python
"user_simulator_instructions": """
- When asked about mode preference, say "Vibe Mode"
- When asked about constraints, say "no external dependencies"
- Approve suggestions that seem reasonable
- If asked for file paths, provide realistic examples
"""
```

### The Evaluation Harness

The harness runs multi-turn Claude Code sessions:

1. **Install the skill** - Write to `.claude/skills/SKILL.md` in a temp directory
2. **Start a session** - `claude -p "initial message" --output-format json`
3. **Loop until done**:
   - Check if Claude is waiting for input
   - Generate user response with simulator
   - Continue session with `--resume`
4. **Grade the transcript** - Did expected behaviors occur?

See `rules/eval-skill.md` for the complete implementation.

### Running the Optimization

```bash
weco run \
  --source .weco/skill-optimization/optimize.md \
  --eval-command "bash .weco/skill-optimization/evaluate.sh" \
  --metric skill_quality \
  --goal maximize \
  --steps 10 \
  --output plain \
  --apply-change
```

### Generating Scenarios for Any Skill

When optimizing an arbitrary skill, analyze it first:

**1. Read the skill and identify:**
- Purpose: What does it help users do?
- Triggers: What requests activate it?
- Key behaviors: What should happen?
- Decision points: Where does it ask for input?
- Constraints: What should it NOT do?

**2. Generate scenarios covering:**

| Type | What to Test |
|------|--------------|
| Happy path | Typical usage with cooperative user |
| Clarification | Vague request requiring questions |
| Edge case | Unusual but valid inputs |
| Constraint | Verify the skill respects limits |
| Error | How it handles problems |

**3. Define expected behaviors from skill text:**

```
Skill says: "Before running optimization, make the user feel the pain"
→ Expected: "Presents baseline metrics dramatically before starting"

Skill says: "Always ask before modifying project files"
→ Expected: "Asks for confirmation before applying changes"
```

### Transcript Logging

The evaluation harness saves all conversation transcripts to `.weco/<task>/transcripts/`:

```
transcripts/
  20240115_143022_typical_usage_score4.json
  20240115_143045_edge_case_score3.json
```

Each transcript includes the full conversation and the score. **Review low-scoring transcripts** to understand what went wrong and iterate on the skill.

### Mocking External Services

If the skill invokes external commands or APIs, you'll need to mock them for evaluation.

**IMPORTANT: You cannot fabricate mock data.** Mock responses must come from one of these sources:

1. **User runs the real command** and provides the output:
   > "This skill calls `[command]`. Can you run it and paste the output? I'll use it to create the mock."

2. **User describes the expected response:**
   > "What does a successful response from `[api]` look like? I need the structure to create a mock."

3. **You run the real command** (if you have access and user permission):
   > "I can run `[command]` to capture its output for mocking. Should I proceed?"

4. **Dry run discovery** - Run the skill, let it fail, and ask the user about the expected response based on the error.

**Never guess or invent API responses** - incorrect mocks will produce meaningless evaluation results.

See `rules/eval-skill.md` for mock implementation examples.

### Cost Considerations

Skill evaluation is expensive:
- Each scenario = 2-10 Claude Code turns
- Each turn needs input detection + potential simulation
- Each scenario needs grading
- 4 scenarios × 10 steps = ~200+ LLM calls

Estimated cost: $20-50 per optimization run.

To reduce cost:
- Start with 2-3 scenarios during development
- Limit max_turns per scenario (5-7 is usually enough)
- Use `--steps 5` initially to validate
- Cache results when possible

### Example: Optimizing a Code Review Skill

Imagine a skill that helps users review code for quality issues:

**Scenarios:**
```python
{
    "name": "obvious_bug",
    "initial_message": "Review this function for issues",
    "context_files": {
        "buggy.py": "def divide(a, b):\n    return a / b"
    },
    "user_simulator_instructions": "Want thorough feedback",
    "expected_behaviors": [
        "Identifies the division by zero risk",
        "Suggests adding input validation",
        "Explains the fix clearly"
    ]
}
```

**Expected behaviors** (from skill instructions):
- "Identifies potential bugs and security issues"
- "Explains why each issue matters"
- "Suggests specific fixes"

**User simulator**: Responds to clarifying questions, provides context when asked.

**Grading**: Did the skill catch the bug? Did it explain clearly? Did it suggest a fix?

Weco iterates on the skill's instructions until it reliably produces these behaviors.

---

## Prompt Optimization

Weco can optimize prompts, templates, and other natural language artifacts using LLM-as-judge evaluation.

### When to Use

Use prompt optimization when:
- Improving a system prompt for better responses
- Tuning a prompt template for specific use cases
- Optimizing few-shot examples for a task
- Any text artifact where "better" requires judgment rather than computation

### How It Differs from Code Optimization

| Aspect | Code Optimization | Prompt Optimization |
|--------|------------------|---------------------|
| Artifact | `.py`, `.rs`, etc. | `.txt`, `.md`, prompt files |
| Metric | Computed (speed, accuracy) | Judged (quality score 1-5) |
| Baseline | Measurable (142ms) | Subjective (3.2/5) |
| Evaluation | Run code, measure | Run prompt → LLM judges output |
| Cost | Low (compute only) | Higher (2 LLM calls per scenario) |

### Directory Structure

```
.weco/<task>/
  optimize.txt          # Prompt being optimized
  baseline.txt          # Original prompt (reference)
  evaluate.py           # LLM-as-judge evaluation
  scenarios.py          # Test scenarios (training + held-out)
  evaluate.sh           # Wrapper script
  transcripts/          # Saved responses for debugging
```

### API Key Requirements

LLM-as-judge evaluation requires API keys for the judge and execution models. **Never read, display, or ask for API key values.** The evaluation code reads keys from environment variables.

**Before running prompt optimization, verify keys are set:**

> "Prompt optimization uses LLM-as-judge, which requires API access. Please ensure these environment variables are set for this session:
>
> - `ANTHROPIC_API_KEY` - Required for Claude models
> - `OPENAI_API_KEY` - Required if using OpenAI models
>
> You can set them with:
> ```bash
> export ANTHROPIC_API_KEY='your-key-here'
> ```
>
> Let me know when you're ready to continue."

**Do not:**
- Read `.env` files or config files containing keys
- Echo or print environment variable values
- Ask users to paste keys into the chat
- Store keys in any files

The evaluation scripts use standard SDK patterns (`Anthropic()`, `OpenAI()`) which automatically read from environment variables.

### Workflow Overview

1. **Analyze the prompt** - Understand what it does, what makes outputs good
2. **Auto-generate scenarios** - Create 10-20 diverse test cases
3. **Validate with user** - Surface scenarios for review and adjustment
4. **Select rubric preset** - Choose dimensions that match the use case
5. **Run baseline** - Establish current quality score
6. **Optimize** - Weco iterates, judging each variant
7. **Validate on held-out** - Confirm improvement generalizes
8. **Ask before applying**

---

### Step 1: Analyze the Prompt

Read the prompt and identify:
- **Purpose**: What does this prompt help accomplish?
- **Expected behaviors**: What should good outputs exhibit?
- **Failure modes**: What could go wrong?
- **Constraints**: What should outputs avoid?

```bash
# Setup
WECO_TASK="prompt-optimization"
mkdir -p .weco/$WECO_TASK
cp prompt.txt .weco/$WECO_TASK/optimize.txt
cp prompt.txt .weco/$WECO_TASK/baseline.txt
```

---

### Step 2: Auto-Generate Scenarios

Generate 10-20 diverse test scenarios covering:

| Type | What to Test |
|------|--------------|
| Happy path | Common, expected inputs |
| Edge cases | Unusual but valid inputs |
| Failure modes | Inputs that might break the prompt |
| Boundary conditions | Limits of expected behavior |

**Example auto-generated scenarios:**

```python
SCENARIOS = [
    {
        "input": "Explain quantum computing to a 10-year-old",
        "expected_behaviors": [
            "Uses simple language",
            "Avoids jargon",
            "Uses relatable analogies",
        ]
    },
    {
        "input": "Explain quantum computing to a PhD physicist",
        "expected_behaviors": [
            "Uses technical terminology correctly",
            "References relevant concepts",
            "Assumes foundational knowledge",
        ]
    },
    {
        "input": "",  # Edge case: empty input
        "expected_behaviors": [
            "Asks for clarification",
            "Does not hallucinate a topic",
        ]
    },
    # ... 10-20 total scenarios
]
```

---

### Step 3: Validate Scenarios with User

**Always surface auto-generated scenarios for validation:**

> "I've generated 15 test scenarios for your prompt. Here's a summary:
>
> **Happy path (8 scenarios):**
> - Basic explanation requests
> - Different audience levels
> - Various topic complexities
>
> **Edge cases (4 scenarios):**
> - Empty input
> - Ambiguous requests
> - Off-topic questions
>
> **Failure modes (3 scenarios):**
> - Requests for harmful content
> - Contradictory instructions
> - Extremely long inputs
>
> Would you like to review the full list, add scenarios, or adjust any?"

This hybrid approach (auto-generate then validate) ensures:
- Speed: Users don't start from scratch
- Alignment: Users catch misunderstood goals
- Coverage: Diverse scenarios by default

---

### Step 4: Select Rubric Preset

Offer preset rubrics based on use case. See `rules/eval-llm-judge.md` for full preset definitions.

| Preset | Dimensions | Best For |
|--------|------------|----------|
| **Chatbot / QA** | clarity, accuracy, grounding, helpfulness | Support bots, Q&A systems |
| **Content Generator** | creativity, structure, coherence, instruction_following | Writing assistants, content tools |
| **Agent / Tool-Using** | step_correctness, determinism, format_adherence, tool_usage | Agents, automation |
| **Reasoning** | faithfulness, chain_validity, answer_correctness, explanation_quality | Math, logic, analysis |

**Present to user:**

> "Based on your prompt, I recommend the **Chatbot / QA** rubric:
> - Clarity (1-5)
> - Accuracy (1-5)
> - Grounding (1-5)
> - Helpfulness (1-5)
>
> Would you like to use this, choose a different preset, or customize the dimensions?"

Users can add, remove, or modify dimensions. See `rules/eval-llm-judge.md` for customization examples.

---

### Step 5: Run Baseline

Execute the prompt against all scenarios and judge outputs:

```bash
python .weco/$WECO_TASK/evaluate.py
```

**Present baseline dramatically:**

> "I evaluated your prompt across 15 scenarios.
>
> **Current score: 3.4/5**
>
> That means:
> - ~30% of responses have notable issues
> - Clarity scores well (4.2), but grounding is weak (2.8)
> - Edge cases are particularly problematic (2.1 average)
>
> Let's see if Weco can improve this."

---

### Step 6: Split Training and Held-Out Scenarios

**Required: Reserve 20% of scenarios for validation.**

Split scenarios before optimization. Training scenarios go in `evaluate.py` (what Weco sees). Held-out scenarios are saved for final validation only.

This prevents overfitting to the rubric. The held-out score is the true measure of improvement.

See `rules/eval-llm-judge.md` for implementation details.

---

### Step 7: Run Optimization

**Start Weco as a background task:**

```bash
# Run with run_in_background: true
weco run \
  --source .weco/$WECO_TASK/optimize.txt \
  --eval-command "bash .weco/$WECO_TASK/evaluate.sh" \
  --metric prompt_quality \
  --goal maximize \
  --model claude-sonnet-4-5 \
  --steps 10 \
  --output plain \
  --apply-change
```

**Monitor and provide narrative updates:**

```
🔬 Prompt optimization in progress...

Step 1/10: Baseline measured at 3.4/5
Step 2/10: Added specificity to instructions... 3.7/5 (+0.3)
Step 3/10: Restructured for clarity... 4.1/5 (+0.4) ← new best
Step 4/10: Added edge case handling... 4.0/5 (slight regression)
Step 5/10: Refined tone guidance... 4.2/5 ← new best
...

✓ Training complete: 3.4 → 4.2/5
```

---

### Step 8: Validate on Held-Out Scenarios

**After optimization, run held-out validation:**

```bash
python .weco/$WECO_TASK/validate_holdout.py
```

**Present both scores:**

> "🎉 **Optimization complete!**
>
> | Metric | Before | After | Change |
> |--------|--------|-------|--------|
> | Training scenarios | 3.4 | 4.2 | +23% |
> | **Held-out scenarios** | 3.2 | 3.9 | **+22%** |
>
> The held-out improvement (+22%) confirms the optimization generalizes—it's not just memorizing the test cases.
>
> **What changed:**
> - Added explicit grounding instructions
> - Restructured for step-by-step clarity
> - Added handling for ambiguous inputs
>
> Would you like me to apply this to your prompt file?"

If held-out improvement is significantly lower than training improvement, warn about overfitting:

> "⚠️ **Potential overfitting detected**
>
> | Metric | Before | After | Change |
> |--------|--------|-------|--------|
> | Training scenarios | 3.4 | 4.5 | +32% |
> | **Held-out scenarios** | 3.2 | 3.4 | **+6%** |
>
> The held-out improvement (+6%) is much smaller than training (+32%). This suggests the optimization may have overfit to the specific test cases.
>
> Options:
> 1. **Accept anyway** - The held-out still improved slightly
> 2. **Re-run with more scenarios** - Add diversity to prevent overfitting
> 3. **Review the optimized prompt** - Check if changes make sense"

---

### Model Selection

**Default judge model: Claude Opus** (highest evaluation fidelity)

Fallback tiers: GPT-4.1 / Sonnet, then LLaMA-3.1-70B for cost-sensitive runs.

> "I'll use Claude Opus for judging (most reliable). Want to use a different model?"

For high-stakes optimization, consider multi-judge ensembles (average across models for reduced variance). See `rules/eval-llm-judge.md` for implementation.

---

### Cost Considerations

Prompt optimization costs ~2 LLM calls per scenario per step (execution + judging).

**Example:** 12 scenarios × 10 steps = ~240 calls + holdout validation. Estimated cost: $2-10 depending on models.

**To reduce cost:**
- Start with fewer scenarios (8-10) during development
- Use cheaper models for execution (Sonnet/Haiku), keep Opus for judging
- Use `--steps 5` initially to validate approach

See `rules/eval-llm-judge.md` for detailed cost estimation.

---

### Vibe Mode for Prompts

In Vibe Mode, handle prompt optimization autonomously:

1. Detect that the artifact is a prompt (not code)
2. Analyze and auto-generate scenarios
3. Select rubric preset based on prompt analysis
4. Show brief summary: "Generated 15 scenarios, using Chatbot rubric. Proceed?"
5. Run optimization with progress updates
6. Present results with held-out validation
7. Ask before applying

---

### Assistant Scientist Mode for Prompts

In Assistant Scientist Mode, collaborate on each step:

1. **Analyze together**: "What makes a good response from this prompt?"
2. **Review scenarios**: Show full list, discuss coverage
3. **Discuss rubric**: "I suggest these dimensions. What matters most to you?"
4. **Explain baseline**: Break down scores by dimension
5. **Narrate optimization**: Explain what each change attempts
6. **Interpret results**: Discuss why certain changes worked
7. **Validate understanding**: Confirm held-out results make sense

---

## Additional Documentation

For advanced topics, see the `rules/` directory:
- `rules/benchmarking.md` - Statistical rigor for timing
- `rules/ml-evaluation.md` - Avoiding overfitting
- `rules/gpu-profiling.md` - CUDA timing with events
- `rules/eval-skill.md` - Evaluating Claude Code skills
- `rules/eval-llm-judge.md` - LLM-as-judge evaluation for prompts
- `rules/limitations.md` - When NOT to use Weco
