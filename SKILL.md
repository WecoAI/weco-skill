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

## Environment Variables and API Keys in Generated Code

When generating scripts that require API keys or other environment variables (e.g., evaluation scripts that call the Anthropic or OpenAI API), **always load from a `.env` file** in addition to standard environment variables. This is the preferred method because:
- Cursor users cannot `export` env vars that persist across terminal sessions
- `.env` files work consistently across Claude Code, Cursor, and standalone execution
- It avoids the agent ever needing to handle keys directly

### Implementation by Language

**Python** — use `python-dotenv`:
```python
# Add at the top of any script that needs API keys/env vars
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
```

**Node.js / TypeScript** — use `dotenv`:
```javascript
// Add at the top of the entry point
require('dotenv').config();
// or for ESM:
import 'dotenv/config';
```

**Bash** — source `.env` directly:
```bash
# Source .env if it exists (for API keys etc.)
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi
```

**Other languages** — use the language's standard dotenv library (e.g., `godotenv` for Go, `dotenvy` for Rust).

### When to Set Up `.env` Loading

- **Automatically**: When generating evaluation scripts or any code that calls external APIs, include `.env` loading by default. Do not ask the user — just add it.
- **`.env` file creation**: If the script needs keys and no `.env` file exists, ask the user to create one and tell you when it's ready:

> "This script needs an API key to run. Please create a `.env` file in your project root with the key for your chosen provider:
>
> ```
> # For Anthropic (default)
> ANTHROPIC_API_KEY=your-key-here
>
> # For OpenAI
> OPENAI_API_KEY=your-key-here
> ```
>
> Let me know when it's set up and I'll continue."

### Safety Rules

- **Never read `.env` contents** — the agent must never `cat .env`, `grep .env`, or inspect the file
- **Never write keys to `.env`** — the user creates and manages this file themselves
- **Ensure `.env` is gitignored** — when creating a `.env` loading pattern, check that `.env` is in `.gitignore`. If not, add it automatically:

```bash
# Add .env to .gitignore if not already present
grep -qxF '.env' .gitignore 2>/dev/null || echo '.env' >> .gitignore
```

### Cursor Sandbox Restrictions

Cursor runs commands in a sandbox that may block file access — including reading `.env` files. This means `.env` can exist and pass a `test -r` check, but `source .env` or `load_dotenv()` will fail at runtime with a permission error.

**Symptoms:**
- `.env` file exists but evaluation fails with `PermissionError` or similar sandbox denial
- `source .env` silently fails or is blocked
- `python-dotenv` raises an error reading `.env`

**Fix:** The user must configure Cursor to allow file access for evaluation scripts. In the Cursor task or agent configuration, set:

```
required_permissions: ['all']
```

Or configure the specific file access permissions needed.

**During pre-flight**, if you detect a sandbox permission error on `.env` access, tell the user immediately:

> "Cursor's sandbox is blocking `.env` file access. Your evaluation scripts need to read `.env` for API keys.
>
> Please update your Cursor configuration to allow file access:
>
> ```
> required_permissions: ['all']
> ```
>
> Then re-run the evaluation. Let me know when it's updated."

Do not retry or debug further until the user confirms the sandbox is configured. Each failed attempt wastes an evaluation run.

---

## Model Reference

Use these model IDs when generating evaluation scripts. **Always use aliases** (not dated snapshot IDs) so scripts stay current.

### Anthropic Models

| Model | API ID | Cost (in/out per MTok) | Use For |
|-------|--------|------------------------|---------|
| Claude Opus 4.6 | `claude-opus-4-6` | $5 / $25 | Best judge model, complex evaluation |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` | $3 / $15 | Default skill/prompt execution, good judge |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1 / $5 | User simulator, input detection, cheap tasks |

**Legacy (still available):**

| Model | API ID | Cost (in/out per MTok) |
|-------|--------|------------------------|
| Claude Sonnet 4 | `claude-sonnet-4-0` | $3 / $15 |
| Claude Haiku 3 | `claude-3-haiku-20240307` | $0.25 / $1.25 |

### OpenAI Models

| Model | API ID | Use For |
|-------|--------|---------|
| GPT-5.2 | `gpt-5.2` | Latest flagship |
| GPT-5 | `gpt-5` | Flagship |
| GPT-5 Mini | `gpt-5-mini` | Cost-effective |
| GPT-5 Nano | `gpt-5-nano` | Cheapest |
| GPT-4.1 | `gpt-4.1` | Reliable, well-tested |
| GPT-4.1 Mini | `gpt-4.1-mini` | Cost-effective |
| GPT-4.1 Nano | `gpt-4.1-nano` | Cheapest |
| GPT-4o | `gpt-4o` | Previous flagship |
| GPT-4o Mini | `gpt-4o-mini` | Previous cost-effective |
| o4 Mini | `o4-mini` | Reasoning |
| o3 | `o3` | Reasoning |

### Default Model Assignments for Evaluation

**Anthropic (default):**

| Role | Default | Why |
|------|---------|-----|
| Skill/prompt execution (agent under test) | `claude-sonnet-4-5` | Good balance of capability and cost |
| User simulator | `claude-haiku-4-5` | Cheap, fast, sufficient for simulation |
| Input detection (`needs_user_input`) | `claude-haiku-4-5` | Binary classification, cheapest model works |
| Transcript/response judge | `claude-sonnet-4-5` | Needs good judgment; upgrade to `claude-opus-4-6` for high-stakes |

**OpenAI alternative:**

| Role | Default | Why |
|------|---------|-----|
| Skill/prompt execution | `gpt-4.1` | Reliable, well-tested |
| User simulator | `gpt-4.1-mini` | Cost-effective |
| Input detection | `gpt-4.1-nano` | Cheapest, sufficient for binary classification |
| Transcript/response judge | `gpt-4.1` | Good judgment; upgrade to `o3` for high-stakes |

Ask the user which provider they prefer. The evaluation templates support both — set `PROVIDER = "anthropic"` or `PROVIDER = "openai"` at the top of the evaluation script.

### Model Validation (Required Before Evaluation)

**Before running any evaluation**, validate that the configured models are available on the user's API key. The evaluation templates include a `validate_models()` function that sends a single-token smoke test to each configured model. If a model fails, tell the user which model is unavailable and suggest alternatives from the table above. Do not proceed with evaluation until all models validate successfully.

### Provider Abstraction

The evaluation templates use a `chat()` helper function that works with both Anthropic and OpenAI. Set `PROVIDER = "anthropic"` or `PROVIDER = "openai"` at the top of the evaluation script:

```python
# =============================================================================
# PROVIDER CONFIGURATION
# =============================================================================

# Set to "anthropic" or "openai"
PROVIDER = "anthropic"


def chat(model, messages, system=None, max_tokens=1024):
    """Send a chat request to the configured provider.

    Works with both Anthropic and OpenAI APIs.
    """
    if PROVIDER == "anthropic":
        from anthropic import Anthropic
        client = Anthropic()
        kwargs = {"model": model, "max_tokens": max_tokens, "messages": messages}
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        return response.content[0].text

    elif PROVIDER == "openai":
        from openai import OpenAI
        client = OpenAI()
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)
        response = client.chat.completions.create(
            model=model, max_tokens=max_tokens, messages=full_messages,
        )
        return response.choices[0].message.content

    else:
        raise ValueError(f"Unknown provider: {PROVIDER}")


def validate_models(*model_ids):
    """Smoke test model availability before running evaluation."""
    all_ok = True
    for model_id in set(model_ids):
        try:
            chat(model_id, [{"role": "user", "content": "hi"}], max_tokens=1)
            print(f"  ok: {model_id}", file=sys.stderr)
        except Exception as e:
            print(f"  FAILED: {model_id} - {e}", file=sys.stderr)
            all_ok = False
    return all_ok
```

All template functions (`run_with_prompt`, `judge_response`, `run_scenario`, etc.) use `chat()` instead of calling the Anthropic or OpenAI client directly.

---

## Environment Pre-flight

**⚠️ REQUIRED: Run this checklist before any evaluation (baseline or optimization). ⚠️**

Environment issues — missing package managers, broken virtual environments, inaccessible `.env` files, missing dependencies — cause evaluation failures that look like optimization failures. Catching them upfront in a single pass prevents cascading debug cycles.

### Pre-flight Checklist

#### 1. Detect Language and Package Manager

Identify what's available in the project environment:

| Language | Check for (in order) | Dependency Files |
|----------|----------------------|-----------------|
| Python | `uv`, `pip`, `poetry`, `conda` | `requirements.txt`, `pyproject.toml`, `setup.py` |
| Node.js | `npm`, `yarn`, `pnpm`, `bun` | `package.json` |
| Rust | `cargo` | `Cargo.toml` |
| Go | `go` | `go.mod` |
| Ruby | `bundle` | `Gemfile` |

```bash
# Example: detect Python package manager
which uv 2>/dev/null && echo "uv" || \
which pip 2>/dev/null && echo "pip" || \
which poetry 2>/dev/null && echo "poetry" || \
which conda 2>/dev/null && echo "conda" || \
echo "NONE"
```

**If no package manager is found**, tell the user what's needed and wait:

> "I need a Python package manager to install evaluation dependencies. Please install one:
>
> - `uv` (recommended): `curl -LsSf https://astral.sh/uv/install.sh | sh`
> - `pip`: Usually included with Python (`python -m ensurepip`)
>
> Let me know when it's ready."

**Record which package manager is available** — you'll need it for dependency installation and for fixing missing packages during optimization.

#### 2. Create Isolated Environment (if applicable)

Some languages need virtual environments to avoid polluting the user's system. Create one inside the task directory:

**Python with uv:**
```bash
cd .weco/<task>
uv venv .venv
source .venv/bin/activate
```

**Python with pip/venv:**
```bash
cd .weco/<task>
python -m venv .venv
source .venv/bin/activate
```

**Python with conda:**
```bash
conda create -p .weco/<task>/.venv python=3.11 -y
conda activate .weco/<task>/.venv
```

**Node.js, Rust, Go, Ruby:** These use project-local dependency management by default (`node_modules/`, `target/`, `vendor/`). No virtual environment needed — skip this step.

**Important:** Always create the environment inside the task directory (`.weco/<task>/.venv`) so it doesn't interfere with the user's project environment.

#### 3. Install Dependencies

Install all packages required by the evaluation script **before** the first run:

**Python:**
```bash
# Install evaluation dependencies
pip install anthropic python-dotenv  # or uv pip install ...

# If the project has a requirements file, install those too
pip install -r requirements.txt 2>/dev/null || true
```

**Node.js:**
```bash
npm install  # or yarn install, pnpm install
```

**Other languages:** Use the standard dependency installation command for the language's package manager.

**Key point:** Install now, not later. Discovering missing packages during optimization step 3 of 10 wastes time and Weco credits.

#### 4. Verify .env Accessibility

Check that `.env` exists and is readable **without reading its contents**:

```bash
# Check .env exists and is readable (NOT its contents)
test -r .env && echo ".env: OK" || \
test -r ../../.env && echo "Project root .env: OK" || \
echo ".env: NOT FOUND"
```

If the evaluation needs API keys and no `.env` is found, prompt the user:

> "The evaluation script needs `ANTHROPIC_API_KEY`. Please create a `.env` file in your project root:
>
> ```
> ANTHROPIC_API_KEY=your-key-here
> ```
>
> Let me know when it's set up."

Do not proceed until `.env` is confirmed accessible.

#### 5. Dry-Run the Evaluation Script

Run the evaluation script once end-to-end as a smoke test:

```bash
bash .weco/<task>/evaluate.sh
```

**Check the output for:**

| Error Pattern | Fix |
|---------------|-----|
| `ModuleNotFoundError` / `Cannot find module` | Install the missing package |
| `PermissionError` / `Permission denied` | `chmod +x` the script, or check sandbox restrictions (see below) |
| `FileNotFoundError` | Check paths, copy missing data files |
| API authentication errors | Prompt user to check `.env` (without reading it) |
| Model not found / unavailable | Fix model ID (see Model Reference above) |
| Sandbox denial on `.env` or venv | **Cursor sandbox** — tell user to set `required_permissions: ['all']` (see "Cursor Sandbox Restrictions" above) |

**Cursor users:** If the dry-run fails with permission errors on `.env` or virtual environment operations, this is almost certainly a sandbox restriction — not a file permission issue. See "Cursor Sandbox Restrictions" in the Environment Variables section above. Do not waste attempts debugging file permissions; address the sandbox configuration first.

**If the dry-run succeeds:** The environment is ready. Proceed with baseline measurement.

**If it fails:** Fix the issue, re-run the dry-run, and repeat until it passes. Do not proceed to baseline or optimization until the dry-run completes successfully.

### Pre-flight in evaluate.sh

The `evaluate.sh` wrapper should handle environment activation automatically so each Weco step runs in the correct environment:

```bash
#!/bin/bash
set -e
cd "$(dirname "$0")"

# Source .env for API keys
if [ -f .env ]; then
    set -a; source .env; set +a
elif [ -f ../../.env ]; then
    set -a; source ../../.env; set +a
fi

# Activate virtual environment if it exists
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
elif [ -f ../../.venv/bin/activate ]; then
    source ../../.venv/bin/activate
fi

python evaluate.py optimize.md
```

Adapt the last line for the project's language (e.g., `node evaluate.js`, `cargo run`, etc.).

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
```

### Step 5: Environment Pre-flight

**Run the full pre-flight checklist** (see "Environment Pre-flight" section above) before generating or running any evaluation:

1. Detect package manager (uv, pip, npm, cargo, etc.)
2. Create isolated environment (`.weco/$WECO_TASK/.venv` for Python)
3. Install evaluation dependencies
4. Verify `.env` is accessible
5. (After generating evaluate.sh in Step 6) Dry-run the evaluation script

Do not proceed to evaluation until the dry-run passes.

### Step 6: Generate Evaluation

**Skip this step if using an existing evaluation script.**

Create an evaluation script based on the inferred goal. Use sensible defaults:

- **Speed**: Benchmark with 10 warmup iterations, 100 timed iterations
- **Accuracy**: Test against available test data or create a validation split
- **Memory**: Profile peak memory usage

**Design a stable interface:** Import and call a well-defined function from the optimized file (e.g., `build_pipeline()`, `train_and_score()`). Avoid `exec()` of code snippets. This creates a clear API contract the optimizer must preserve. See `rules/evaluate.md` for details.

Write the evaluation script and wrapper automatically.

### Step 7: Run Optimization with Async Monitoring

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
| `PermissionError` on scripts | Run `chmod +x <file>` |
| `PermissionError` on `.env` or venv | **Cursor sandbox** — stop the run, tell user to set `required_permissions: ['all']`, then restart |

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

### Step 8: Celebrate Wins Dramatically

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

### Step 9: Ask Before Applying

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

### Phase 3: Environment Pre-flight

**Run the full pre-flight checklist** (see "Environment Pre-flight" section above):

1. Detect package manager
2. Create isolated environment (`.weco/<task>/.venv` for Python, etc.)
3. Install evaluation dependencies
4. Verify `.env` is accessible
5. Dry-run the evaluation script after it's created

Discuss any issues with the user as you go:

> "I'm setting up the evaluation environment. I'll need to install `anthropic` and `python-dotenv` — is that OK?"

Do not proceed to baseline measurement until the dry-run passes.

### Phase 4: Establish the Baseline

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

### Phase 5: Code Analysis

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

### Phase 6: Evaluation Alignment

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

### Phase 7: Small Run Validation

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

### Phase 8: Full Optimization with Async Monitoring

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
| `PermissionError` on scripts | Run `chmod +x <file>` |
| `PermissionError` on `.env` or venv | **Cursor sandbox** — stop the run, tell user to set `required_permissions: ['all']`, then restart |

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

### Phase 9: Results, Report, and Insights

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

### Phase 10: Integration

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

Weco can optimize agent skills themselves. This is meta-optimization: using Weco to improve the instructions that guide an agent's behavior. This works with skills for Claude Code, Cursor, or any agent that uses system prompts.

**⚠️ IMPORTANT: Before starting skill optimization, you MUST read `rules/eval-skill.md` in full.** It contains the complete evaluation harness implementation, scenario generation guidelines, and statistical validation procedures. Do not attempt to implement skill evaluation from memory or from the summaries below — read the rule file first.

### When to Use

Use skill optimization when:
- A skill isn't producing the desired behaviors
- You want to improve how a skill handles edge cases
- The skill needs to be more robust across different user types
- You're developing a new skill and want to iterate quickly

### How It Works

1. **Analyze the skill** - Understand what behaviors it should produce
2. **Check for tool dependencies** - Identify if the skill relies on tool execution (see below)
3. **Generate test scenarios** - Create realistic multi-turn conversations with a difficulty gradient
4. **Run conversations** - Execute the skill as a system prompt via API, simulating multi-turn interactions
5. **Grade transcripts** - Use an LLM judge to evaluate if expected behaviors occurred
6. **Iterate** - Weco modifies the skill and re-evaluates

### Tool Dependency Check

**Before building the evaluation harness**, check if the skill relies heavily on tool execution. Look for:
- References to specific scripts or functions (e.g., `analyze.py`, `summarize_csv()`)
- Instructions that assume file system access
- Workflows that depend on command execution

If tool-dependent, warn the user:

> "This skill relies on `[tool/script]` for core functionality. The API-based evaluation can test conversational behavior but **cannot execute actual tools**.
>
> Options:
> 1. **Behavioral optimization only** — Evaluate workflow, communication, decision-making
> 2. **Add tool definitions** — Include tool schemas so the model produces tool_use blocks
> 3. **Split optimization** — Optimize conversational behavior here, optimize tool code separately with standard Weco code optimization
>
> Which approach would you prefer?"

**Do not build the evaluation harness before resolving this.** See `rules/eval-skill.md` for details.

### Quick Setup

```bash
# Create task directory
mkdir -p .weco/skill-optimization

# Copy the skill to optimize
cp path/to/SKILL.md .weco/skill-optimization/optimize.md
cp path/to/SKILL.md .weco/skill-optimization/baseline.md
```

### Handling Rules

Skills often have associated rules in a `rules/` directory. Copy them to the optimization directory so they can be included in the system prompt during evaluation:

```bash
# Copy rules so they're included in the system prompt during evaluation
cp -r path/to/rules/ .weco/skill-optimization/rules/
```

During evaluation, rules are concatenated with the skill content to form the system prompt, matching how agents load rules in practice.

**Important:** Only SKILL.md is optimized. Rules are reference material included in the system prompt, not optimization targets. Weco modifies `optimize.md` (the skill) while rules remain unchanged in the `rules/` directory.

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

### API Key Requirements

Skill evaluation uses the Anthropic or OpenAI API (depending on provider configuration) for conversations, simulation, and grading. **Never read, check, or handle API keys.** If evaluation fails due to a missing key, tell the user to create a `.env` file with `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`) and let you know when it's ready. See "Environment Variables and API Keys in Generated Code" above for the general approach.

### The Evaluation Harness

The harness runs multi-turn conversations via the configured provider's API (Anthropic or OpenAI):

1. **Load the skill as system prompt** - Skill content (plus any rules) becomes the system prompt
2. **Send initial message** - `chat(model, messages, system=skill)`
3. **Loop until done**:
   - Check if the assistant is waiting for user input
   - Generate simulated user response via API
   - Continue conversation with accumulated messages
4. **Grade the transcript** - Did expected behaviors occur?

**Read `rules/eval-skill.md` for the complete implementation** — it contains the harness code, simulator, grader, and scenario templates you need to create these files.

### Variance Check Before Optimization

---

**⚠️ REQUIRED GATE: This is not optional ⚠️**

You MUST measure baseline variance before running optimization. Do not skip this step. Without variance measurement, you cannot interpret whether optimization results are real improvements or noise.

---

Skill evaluation has high variance due to multi-turn conversations. **Measure baseline standard deviation before optimizing.**

**Ask how many runs:**

> "Before optimizing, I need to measure evaluation stability. How many baseline runs would you like?
> - **3 runs** (Recommended minimum)
> - **5 runs** (Better estimate)
>
> Skill evaluation is expensive, so 3-5 runs is usually a good balance."

```bash
# Run baseline N times (minimum 3)
for i in $(seq 1 $NUM_RUNS); do
  python .weco/skill-optimization/evaluate.py
done
```

> "Baseline scores: 3.6, 3.8, 3.5, 3.7, 3.6 (std dev: 0.11)
>
> Variance is low — evaluation is stable enough to proceed with optimization."

---

**⚠️ VARIANCE CHECK: Gate before optimization ⚠️**

If standard deviation is high (>0.3 on a 5-point scale), **warn the user and suggest fixes before proceeding:**

> "⚠️ **High evaluation variance detected**
>
> Your baseline scored 3.2, 3.8, and 3.5 across three runs (std dev: 0.3).
>
> With this much variance, a +0.3 improvement could just be noise. Before optimizing, I recommend:
>
> 1. **Add more scenarios** to get more stable signal
> 2. **Make expected_behaviors more specific** to reduce grading ambiguity
> 3. **Simplify user_simulator_instructions** for more consistent conversations
>
> Want to proceed anyway, or address the variance first?"

**Do not proceed without acknowledgment if std dev > 0.3.**

---

### Held-Out Scenarios (Required)

Split scenarios before optimization:

```python
TRAINING_SCENARIOS = SCENARIOS[:4]  # Optimizer sees these
HOLDOUT_SCENARIOS = SCENARIOS[4:]   # For final validation only
```

After optimization, validate on held-out scenarios to confirm improvement is real.

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

### Validating Results

After optimization completes, run a single held-out validation:

```bash
python .weco/skill-optimization/validate_holdout.py
```

**Compare improvement to std dev:**

> "Training improved: 3.6 → 4.0 (+0.4)
> Held-out score: 3.8 (baseline: 3.5, improvement: +0.3)
> Baseline std dev: 0.15
>
> **Confidence: HIGH** - Improvement (0.3) is 2× std dev (0.15). This improvement is likely real."

If held-out improvement < 2× baseline std dev, the improvement may be noise.

### Generating Scenarios for Any Skill

When optimizing an arbitrary skill, analyze it first. See `rules/eval-skill.md` for the full scenario generation procedure.

**1. Read the skill and identify:**
- Purpose: What does it help users do?
- Triggers: What requests activate it?
- Key behaviors: What should happen?
- Decision points: Where does it ask for input?
- Constraints: What should it NOT do?
- **Weaknesses**: Where are instructions vague, incomplete, or ambiguous?

**2. Generate scenarios with a difficulty gradient:**

| Difficulty | % of Scenarios | Purpose |
|------------|----------------|---------|
| Easy | ~30% | Sanity checks, should score 4-5/5 on baseline |
| Medium | ~40% | Quality of execution, should score 3-4/5 |
| Hard | ~30% | Target weaknesses and gaps, should score 2-3/5 |

**At least 2 scenarios MUST target areas where the current skill is likely to fail.** If the baseline scores 4.5+ on all scenarios, they are too easy.

**3. Define expected behaviors that test quality, not just presence:**

```
# Bad - trivially satisfied
"Analyzes the code"

# Good - requires quality
"Identifies at least 2 specific bottlenecks with quantitative reasoning"

# Good - tests adaptation
"Adapts explanation depth to the user's apparent expertise level"
```

### Transcript Logging

The evaluation harness saves all conversation transcripts to `.weco/<task>/transcripts/`:

```
transcripts/
  20240115_143022_typical_usage_score4.json
  20240115_143045_edge_case_score3.json
```

Each transcript includes the full conversation and the score. **Review low-scoring transcripts** to understand what went wrong and iterate on the skill.

### External Services

The API-based evaluation runs the skill as a system prompt without tool access. The model describes what it *would* do (read files, run commands, etc.) rather than actually executing tools. The grader evaluates whether the model describes the correct behavior:

```python
# The grader checks behavioral intent, not execution
expected_behaviors = [
    "Describes running weco with the correct flags",
    "Mentions checking for existing evaluation scripts",
    "Says it will back up the original file",
]
```

This works well for evaluating conversational behavior, workflow adherence, and constraint compliance. See `rules/eval-skill.md` for details on limitations.

### Cost Considerations

Skill evaluation is expensive:
- Each scenario = 2-10 API calls for multi-turn conversation
- Each turn needs input detection + potential simulation
- Each scenario needs grading
- 4 scenarios x 10 steps = ~200+ LLM calls

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

**⚠️ IMPORTANT: Before starting prompt optimization, you MUST read `rules/eval-llm-judge.md` in full.** It contains the complete LLM-as-judge evaluation template, rubric presets, variance estimation procedures, and validation logic. Do not attempt to implement prompt evaluation from memory or from the summaries below — read the rule file first.

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

LLM-as-judge evaluation requires `ANTHROPIC_API_KEY` (and `OPENAI_API_KEY` if using OpenAI models).

**The agent must NEVER read, check, display, or handle API keys in any way.** Do not run commands like `echo $ANTHROPIC_API_KEY`, `env | grep KEY`, `printenv`, or read `.env` file contents. Do not ask users to paste keys into the chat. Do not write keys to any files.

If the evaluation scripts fail due to a missing key, tell the user to create a `.env` file:

> "The evaluation requires `ANTHROPIC_API_KEY`. Please add it to a `.env` file in your project root:
>
> ```
> ANTHROPIC_API_KEY=your-key-here
> ```
>
> Let me know when it's set up and I'll continue."

See "Environment Variables and API Keys in Generated Code" above for the general approach. The agent should never be involved in key setup beyond this message.

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

### Step 1: Analyze the Prompt and Gather Context

Read the prompt and identify:
- **Purpose**: What does this prompt help accomplish?
- **Expected behaviors**: What should good outputs exhibit?
- **Failure modes**: What could go wrong?
- **Constraints**: What should outputs avoid?

**Detect if domain examples are needed:**

Some optimization tasks require concrete examples of "good" output. The optimizer cannot improve style, tone, or domain-specific quality without seeing what success looks like.

| Task Type | Examples Needed? |
|-----------|------------------|
| Style matching / impersonation | Yes - need example outputs in the target style |
| Brand voice | Yes - need examples of on-brand writing |
| Domain-specific accuracy | Yes - need correct examples for the domain |
| General clarity/helpfulness | No - generic rubric usually sufficient |

**If examples are needed, request them:**

> "For this kind of optimization, I need to see what 'good' looks like. Can you share 3-5 examples of ideal outputs?
>
> For example:
> - If this is an impersonation prompt, share messages written by the person being impersonated
> - If this is brand voice, share approved copy that nails the tone
> - If this is domain-specific, share correct answers from an expert
>
> Without these, the optimizer can only apply generic improvements—it won't know what makes outputs good *for your specific use case*."

**Store examples for use in evaluation:**

```python
# Include in scenarios.py
REFERENCE_EXAMPLES = [
    {
        "input": "User request that was handled well",
        "ideal_output": "The actual good response to learn from",
    },
    # Add 3-5 examples
]
```

These examples can be used as:
1. Few-shot examples in the judge prompt ("outputs should resemble these examples")
2. Reference material for the rubric ("does the output match the style of the examples?")
3. Similarity scoring (how close is the output to the reference style?)

---

**Setup:**

```bash
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

Execute the prompt against all scenarios and judge outputs **multiple times** to estimate variance.

**Ask how many runs to use:**

> "Before optimizing, I need to measure how stable the evaluation is. This helps us know if improvements are real or just noise.
>
> How many baseline runs would you like?
> - **3 runs** (Recommended minimum) - Quick, gives rough estimate
> - **5 runs** - Better confidence in the variance estimate
> - **10 runs** - High confidence, but costs more
>
> More runs = more accurate variance estimate = better ability to detect real improvements."

```bash
# Run baseline N times (minimum 3)
for i in $(seq 1 $NUM_RUNS); do
  python .weco/$WECO_TASK/evaluate.py
done
```

**Calculate and present standard deviation:**

```python
import statistics
scores = [3.6, 3.8, 3.7, 3.5, 3.9]  # From N runs
mean = statistics.mean(scores)
std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
```

> "I ran the baseline 5 times to measure evaluation stability.
>
> **Baseline score: 3.7/5** (std dev: 0.15)
>
> Variance is low — evaluation is stable enough to proceed with optimization."

---

**⚠️ VARIANCE CHECK: Gate before optimization ⚠️**

If standard deviation is high (>0.3 on a 5-point scale), **warn the user and suggest fixes before proceeding:**

> "⚠️ **High evaluation variance detected**
>
> Your baseline scored 3.2, 3.8, and 3.5 across three runs (std dev: 0.3).
>
> With this much variance, a +0.3 improvement could just be noise. Before optimizing, I recommend:
>
> 1. **Add more scenarios** (currently 8 → try 15-20) to get more stable signal
> 2. **Add reference examples** if this is style/domain-specific optimization
> 3. **Review scenarios** for ambiguous cases that might score inconsistently
>
> Want to proceed anyway, or address the variance first?"

**Do not proceed without acknowledgment if std dev > 0.3.**

---

### Step 6: Split Training and Held-Out Scenarios

---

**⚠️ REQUIRED GATE: This is not optional ⚠️**

You MUST split scenarios before optimization. Do not skip this step.

---

**Reserve 20% of scenarios for validation:**

Split scenarios before optimization. Training scenarios go in `evaluate.py` (what Weco optimizes against). Held-out scenarios are saved for final validation only.

```python
# This split MUST happen before optimization
import random
random.seed(42)
random.shuffle(ALL_SCENARIOS)
split = int(len(ALL_SCENARIOS) * 0.8)
TRAINING = ALL_SCENARIOS[:split]   # Used during optimization
HOLDOUT = ALL_SCENARIOS[split:]    # Used ONLY for final validation
```

> "I've split your 15 scenarios:
> - **12 for training** (what the optimizer sees)
> - **3 held out** (for validating the improvement is real)
>
> This prevents the optimizer from gaming the test—held-out performance is the true measure."

**Do not skip this step.** Without held-out validation, you cannot distinguish real improvement from overfitting.

Read `rules/eval-llm-judge.md` for the splitting and validation implementation.

---

### Step 7: Run Optimization

Each optimization step runs a single evaluation across all training scenarios. The baseline variance measurement (Step 5) establishes the noise floor; subsequent evaluations use one run each.

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

Step 1/10: Baseline measured at 3.7/5
Step 2/10: Added specificity to instructions... 3.9/5 (+0.2)
Step 3/10: Restructured for clarity... 4.1/5 (+0.2) ← new best
Step 4/10: Added edge case handling... 4.0/5 (slight regression)
Step 5/10: Refined tone guidance... 4.2/5 ← new best
...

✓ Training complete: 3.7 → 4.2/5
```

---

### Step 8: Validate on Held-Out and Assess Confidence

**After optimization, run a single held-out validation:**

```bash
python .weco/$WECO_TASK/validate_holdout.py
```

**Compare improvement to measured standard deviation:**

Remember the baseline std dev you measured in Step 5. Compare the improvement magnitude to that std dev:

| Improvement vs Std Dev | Confidence |
|------------------------|------------|
| Improvement > 2× std dev | High - likely real |
| Improvement ≈ 1-2× std dev | Moderate - possibly real |
| Improvement < std dev | Low - may be noise |

---

**If improvement is statistically significant (improvement > 2× std dev):**

> "🎉 **Optimization complete!**
>
> | Metric | Before | After | Change |
> |--------|--------|-------|--------|
> | Training scenarios | 3.4 | 4.2 | +0.8 |
> | **Held-out scenarios** | 3.2 | 3.9 | **+0.7** |
> | Baseline std dev | ±0.1 | | |
>
> **Statistical confidence: HIGH** ✓
>
> The held-out improvement (+0.7) is 7× your baseline std dev (0.1). This improvement is almost certainly real, not noise.
>
> **What changed:**
> - Added explicit grounding instructions
> - Restructured for step-by-step clarity
> - Added handling for ambiguous inputs
>
> Would you like me to apply this to your prompt file?"

---

**If improvement is within noise range (improvement < 2× std dev):**

> "⚠️ **Improvement may not be statistically significant**
>
> | Metric | Before | After | Change |
> |--------|--------|-------|--------|
> | Training scenarios | 3.6 | 3.9 | +0.3 |
> | **Held-out scenarios** | 3.5 | 3.7 | **+0.2** |
> | Baseline std dev | ±0.2 | | |
>
> **Statistical confidence: LOW** ⚠️
>
> The held-out improvement (+0.2) is only 1× your baseline std dev (0.2). This could be noise rather than real improvement.
>
> **Options:**
> 1. **Strengthen the signal** - Add more scenarios or reference examples
> 2. **Run longer** - More optimization steps may find clearer improvements
> 3. **Accept with caution** - The changes may still be directionally useful
> 4. **Review changes manually** - Check if the edits make intuitive sense"

---

**If held-out improvement is much lower than training (overfitting):**

> "⚠️ **Potential overfitting detected**
>
> | Metric | Before | After | Change |
> |--------|--------|-------|--------|
> | Training scenarios | 3.4 | 4.5 | +32% |
> | **Held-out scenarios** | 3.2 | 3.4 | **+6%** |
>
> The held-out improvement (+6%) is much smaller than training (+32%). The optimizer may have gamed the training scenarios.
>
> **Options:**
> 1. **Add scenario diversity** - More varied test cases prevent overfitting
> 2. **Review the optimized prompt** - Check if changes are superficial
> 3. **Accept with caution** - Some improvement is better than none"

---

### Step 9: Next Steps

After showing results, offer paths to continue:

> "**What would you like to do next?**
>
> 1. **Apply changes** - Use the optimized prompt
> 2. **Run more steps** - Continue optimizing from here
> 3. **Add more scenarios** - Improve evaluation coverage
> 4. **Adjust rubric** - Reweight dimensions that matter most
> 5. **Discard** - Keep the original prompt"

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
- `rules/eval-skill.md` - Evaluating agent skills (Claude Code, Cursor, etc.)
- `rules/eval-llm-judge.md` - LLM-as-judge evaluation for prompts
- `rules/limitations.md` - When NOT to use Weco
