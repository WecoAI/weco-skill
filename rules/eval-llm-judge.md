---
name: eval-llm-judge
description: LLM-as-judge evaluation for prompts, skills, and natural language artifacts
metadata:
  tags: llm, judge, prompt, skill, natural-language, quality
---

## When to Use

Use LLM-as-judge evaluation when optimizing:
- Prompts and system instructions
- Agent skills and workflows
- Templates and natural language artifacts
- Any output where "better" requires judgment rather than computation

## Critical Rules

1. **Use structured JSON output** - The judge must return parseable scores
2. **Design independent dimensions** - Each rubric dimension should measure one thing
3. **Use diverse test scenarios** - Cover edge cases, common cases, and failure modes
4. **Measure baseline variance** - Required before optimization to establish significance threshold
5. **Never read, check, or handle API keys** - Keys must be set by the user before launching the agent

## API Key Handling

LLM-as-judge requires API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.).

**The agent must NEVER read, check, display, or handle API keys in any way.** Do not run commands like `echo $ANTHROPIC_API_KEY`, `env | grep KEY`, `printenv`, or read `.env` file contents. Do not ask users to paste keys into the chat. Do not write keys to any files.

The evaluation scripts load from `.env` via `python-dotenv` and the `evaluate.sh` wrapper also sources `.env`. If evaluation fails due to a missing key, tell the user to create a `.env` file:

> "The evaluation requires `ANTHROPIC_API_KEY`. Please add it to a `.env` file in your project root:
>
> ```
> ANTHROPIC_API_KEY=your-key-here
> ```
>
> Let me know when it's set up and I'll continue."

The agent should never be involved in key setup beyond this message.

**Cursor sandbox note:** Cursor's sandbox may block `.env` file reads even when the file exists. If evaluation fails with permission errors on `.env`, tell the user to set `required_permissions: ['all']` in their Cursor configuration and re-run. Do not retry without this fix — each attempt wastes an evaluation run.

## Template

See [assets/evaluate-llm-judge.py](../assets/evaluate-llm-judge.py) for the complete template.

```python
"""Evaluate prompt quality using LLM-as-judge.

This runs a single evaluation. Weco calls this once per optimization step.
Statistical rigor is handled by:
1. Baseline variance measurement (before optimization)
2. Progressive held-out validation (after optimization)
"""
import json
import sys
from pathlib import Path

# Load API keys from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from anthropic import Anthropic

# Resolve paths relative to this script's directory
SCRIPT_DIR = Path(__file__).parent

def load_artifact(path):
    return Path(path).read_text()

# Load the prompt being optimized (same directory as this script)
optimized = load_artifact(SCRIPT_DIR / "optimize.txt")

# Training scenarios only - held-out scenarios used for final validation
TRAINING_SCENARIOS = [
    {
        "input": "User request or context here",
        "expected_behaviors": ["behavior1", "behavior2"],
    },
    # Add scenarios covering:
    # - Common use cases
    # - Edge cases
    # - Potential failure modes
]

# Judge prompt with structured rubric
JUDGE_PROMPT = """
You are evaluating a prompt's effectiveness based on the response it produced.

## Rubric

Rate each dimension 1-5:

1. **Clarity** (1-5): Is the response clear and unambiguous?
2. **Completeness** (1-5): Does it address all aspects of the request?
3. **Correctness** (1-5): Is the information/behavior accurate?
4. **Helpfulness** (1-5): Does it effectively help the user?

## Expected Behaviors

The response should exhibit: {expected_behaviors}

## Output Format

Return ONLY valid JSON:
{{
  "reasoning": "<brief explanation>",
  "scores": {{
    "clarity": <1-5>,
    "completeness": <1-5>,
    "correctness": <1-5>,
    "helpfulness": <1-5>
  }},
  "overall": <1-5>
}}
"""

# Model configuration - use aliases, not dated snapshot IDs
EXECUTION_MODEL = "claude-sonnet-4-5"
JUDGE_MODEL = "claude-sonnet-4-5"

def validate_models(client, *model_ids):
    """Smoke test model availability before running evaluation."""
    all_ok = True
    for model_id in set(model_ids):
        try:
            client.messages.create(
                model=model_id, max_tokens=1,
                messages=[{"role": "user", "content": "hi"}],
            )
            print(f"  ok: {model_id}", file=sys.stderr)
        except Exception as e:
            print(f"  FAILED: {model_id} - {e}", file=sys.stderr)
            all_ok = False
    return all_ok

def run_with_prompt(prompt, scenario):
    """Execute the prompt being optimized against a scenario."""
    client = Anthropic()
    response = client.messages.create(
        model=EXECUTION_MODEL,
        max_tokens=1024,
        system=prompt,
        messages=[{"role": "user", "content": scenario["input"]}],
    )
    return response.content[0].text

def judge_response(scenario, response):
    """Have a capable LLM judge the response quality."""
    client = Anthropic()
    judge_input = JUDGE_PROMPT.format(
        expected_behaviors=scenario["expected_behaviors"]
    )
    result = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"{judge_input}\n\n## Response to Evaluate\n\n{response}"
        }],
    )
    return json.loads(result.content[0].text)

# Validate models before running scenarios
print("Validating model availability...", file=sys.stderr)
if not validate_models(Anthropic(), EXECUTION_MODEL, JUDGE_MODEL):
    print("Error: One or more models unavailable. Fix model config.", file=sys.stderr)
    print("prompt_quality: 0.00")
    sys.exit(1)

# Single evaluation - Weco handles optimization, validation handles rigor
total_score = 0
for scenario in TRAINING_SCENARIOS:
    response = run_with_prompt(optimized, scenario)
    judgment = judge_response(scenario, response)
    total_score += judgment["overall"]

avg_score = total_score / len(TRAINING_SCENARIOS)
print(f"prompt_quality: {avg_score:.2f}")
```

## Rubric Presets

Use these battle-tested presets for common use cases. Each has 4 independent dimensions optimized for that domain.

### Chatbot / QA Assistant

```python
RUBRIC_PRESET_CHATBOT = {
    "name": "chatbot",
    "dimensions": {
        "clarity": {
            "description": "Is the response clear and unambiguous?",
            "scoring": {
                5: "Crystal clear, no room for misinterpretation",
                3: "Mostly clear with minor ambiguities",
                1: "Confusing or contradictory",
            }
        },
        "accuracy": {
            "description": "Is the information factually correct?",
            "scoring": {
                5: "Fully accurate, no errors",
                3: "Mostly correct with minor issues",
                1: "Contains significant errors or hallucinations",
            }
        },
        "grounding": {
            "description": "Does it stay within what it actually knows?",
            "scoring": {
                5: "Only states what it knows, acknowledges uncertainty",
                3: "Mostly grounded, occasional overreach",
                1: "Makes up information or answers unknowable questions",
            }
        },
        "helpfulness": {
            "description": "Does it address what the user actually needs?",
            "scoring": {
                5: "Directly addresses the need, anticipates follow-ups",
                3: "Addresses the main point, misses nuances",
                1: "Misses the point or is unhelpful",
            }
        },
    }
}
```

### Content Generator

```python
RUBRIC_PRESET_CONTENT = {
    "name": "content",
    "dimensions": {
        "creativity": {
            "description": "Is the content original and engaging?",
            "scoring": {
                5: "Fresh, surprising, captures attention",
                3: "Competent but predictable",
                1: "Generic, boring, or derivative",
            }
        },
        "structure": {
            "description": "Is it well-organized and flows logically?",
            "scoring": {
                5: "Clear structure, smooth transitions, logical flow",
                3: "Adequate organization, some rough transitions",
                1: "Disorganized, hard to follow",
            }
        },
        "coherence": {
            "description": "Does it maintain consistent style and tone?",
            "scoring": {
                5: "Consistent voice throughout",
                3: "Mostly consistent with minor shifts",
                1: "Inconsistent tone, jarring shifts",
            }
        },
        "instruction_following": {
            "description": "Does it follow the given instructions?",
            "scoring": {
                5: "Follows all instructions precisely",
                3: "Follows most instructions, minor deviations",
                1: "Ignores or misinterprets instructions",
            }
        },
    }
}
```

### Agent / Tool-Using System

```python
RUBRIC_PRESET_AGENT = {
    "name": "agent",
    "dimensions": {
        "step_correctness": {
            "description": "Are the steps logically correct?",
            "scoring": {
                5: "All steps are correct and in proper order",
                3: "Mostly correct, minor logical issues",
                1: "Incorrect steps or wrong order",
            }
        },
        "determinism": {
            "description": "Is the behavior predictable and consistent?",
            "scoring": {
                5: "Same input produces same approach every time",
                3: "Generally consistent with minor variation",
                1: "Unpredictable, inconsistent behavior",
            }
        },
        "format_adherence": {
            "description": "Does output match expected format?",
            "scoring": {
                5: "Exactly matches expected format",
                3: "Close to expected format, minor deviations",
                1: "Wrong format, hard to parse",
            }
        },
        "tool_usage": {
            "description": "Are tools used appropriately?",
            "scoring": {
                5: "Correct tools, correct parameters, correct timing",
                3: "Right tools, minor parameter issues",
                1: "Wrong tools or misuse of tools",
            }
        },
    }
}
```

### Reasoning Tasks

```python
RUBRIC_PRESET_REASONING = {
    "name": "reasoning",
    "dimensions": {
        "faithfulness": {
            "description": "Does reasoning follow from premises?",
            "scoring": {
                5: "All conclusions follow logically from stated premises",
                3: "Most reasoning is sound, minor leaps",
                1: "Conclusions don't follow from premises",
            }
        },
        "chain_validity": {
            "description": "Is the chain-of-thought logical?",
            "scoring": {
                5: "Each step follows from the previous",
                3: "Generally logical with some gaps",
                1: "Broken chain, non-sequiturs",
            }
        },
        "answer_correctness": {
            "description": "Is the final answer correct?",
            "scoring": {
                5: "Correct answer",
                3: "Partially correct or close",
                1: "Wrong answer",
            }
        },
        "explanation_quality": {
            "description": "Is the reasoning well-explained?",
            "scoring": {
                5: "Clear, complete explanation a human could follow",
                3: "Adequate explanation, some gaps",
                1: "Poor or missing explanation",
            }
        },
    }
}

# All presets for easy access
RUBRIC_PRESETS = {
    "chatbot": RUBRIC_PRESET_CHATBOT,
    "content": RUBRIC_PRESET_CONTENT,
    "agent": RUBRIC_PRESET_AGENT,
    "reasoning": RUBRIC_PRESET_REASONING,
}
```

### Customizing Presets

Start with a preset and modify as needed:

```python
# Start with chatbot preset
rubric = RUBRIC_PRESETS["chatbot"].copy()

# Add a custom dimension
rubric["dimensions"]["brand_voice"] = {
    "description": "Does it match our brand tone?",
    "scoring": {5: "Perfect brand match", 3: "Close", 1: "Off-brand"}
}

# Remove a dimension that doesn't apply
del rubric["dimensions"]["grounding"]
```

## Judge Prompt Design

### Structure

A good judge prompt has:
1. **Clear role** - "You are evaluating..."
2. **Rubric with dimensions** - 3-5 independent, measurable criteria
3. **Expected behaviors** - What the response should do
4. **Reasoning requirement** - Forces the judge to justify scores
5. **Structured output** - JSON for reliable parsing

## Variance Estimation (Required Before Optimization)

---

**⚠️ REQUIRED GATE: This is not optional ⚠️**

You MUST measure baseline variance before running optimization. Do not skip this step. Without variance measurement, you cannot know whether optimization results are real improvements or noise.

---

LLM-as-judge evaluation has inherent variance. **You must measure this variance before optimization** to establish the significance threshold.

### Measuring Baseline

Run the full evaluation multiple times before optimizing. Ask the user how many runs:

| Runs | Confidence | Recommendation |
|------|------------|----------------|
| 3 | Acceptable | Minimum for reliable estimate |
| 5 | Good | Recommended default |

```python
import statistics
import math

def measure_baseline(prompt_path, scenarios, runs=5):
    """Measure baseline mean and variance.

    Args:
        runs: Number of evaluation runs. Minimum 3.
    """
    if runs < 3:
        raise ValueError("Need at least 3 runs for reliable std dev")

    scores = []
    for i in range(runs):
        print(f"Baseline run {i + 1}/{runs}...")
        total = 0
        for scenario in scenarios:
            response = run_with_prompt(prompt_path, scenario)
            judgment = judge_response(scenario, response)
            total += judgment["overall"]
        run_score = total / len(scenarios)
        scores.append(run_score)
        print(f"  Score: {run_score:.2f}")

    mean = statistics.mean(scores)
    std_dev = statistics.stdev(scores)
    std_err = std_dev / math.sqrt(runs)

    return {
        "mean": mean,
        "scores": scores,
        "std_dev": std_dev,
        "std_err": std_err,
        "n_runs": runs,
    }

# Example output:
# {"mean": 3.7, "scores": [3.6, 3.8, 3.7, 3.5, 3.9], "std_dev": 0.15, "std_err": 0.07, "n_runs": 5}
```

### Interpreting Baseline Variance

| Std Dev | Quality | Recommendation |
|---------|---------|----------------|
| < 0.15 | Excellent | Good to proceed |
| 0.15 - 0.3 | Acceptable | Proceed with caution |
| > 0.3 | High | Add scenarios or simplify before optimizing |

If variance is high (> 0.3), **warn the user and suggest fixes before proceeding.** Do not proceed without user acknowledgment. Suggest:
- Adding more scenarios (15-20 provide more stable signal than 5)
- Using more capable models for judging
- Adding reference examples for domain-specific tasks
- Reviewing scenarios for ambiguous cases

## Reducing Variance

LLM outputs are non-deterministic. To get stable metrics:

1. **Use capable models** - Claude Opus or GPT-4o for judging
2. **More scenarios** - 15-20 scenarios provide more stable signal than 5
3. **Structured output** - JSON reduces parsing failures
4. **Add reference examples** - For style/domain tasks, examples reduce ambiguity

## Test Scenario Design

### Coverage

Ensure scenarios cover:
- **Happy path** - Common, expected use cases
- **Edge cases** - Unusual but valid inputs
- **Failure modes** - Inputs that might break the prompt
- **Boundary conditions** - Limits of expected behavior

### Expected Behaviors

Be specific about what you want:

```python
# Bad - too vague
{"input": "Help me with code", "expected_behaviors": ["be helpful"]}

# Good - specific and measurable
{
    "input": "Help me optimize this sorting function for speed",
    "expected_behaviors": [
        "asks clarifying questions about constraints",
        "measures baseline performance",
        "explains the optimization approach",
        "asks before applying changes"
    ]
}
```

## Reference Examples for Domain-Specific Optimization

For style matching, impersonation, brand voice, or domain-specific tasks, **generic rubrics are insufficient**. The optimizer needs concrete examples of "good" output.

### When Reference Examples Are Required

| Task Type | Examples Needed? | What to Collect |
|-----------|------------------|-----------------|
| Style/impersonation | Yes | Messages written by the target person |
| Brand voice | Yes | Approved copy that exemplifies the tone |
| Domain accuracy | Yes | Expert-verified correct answers |
| General helpfulness | No | Generic rubric usually sufficient |

### How to Use Reference Examples

**Option 1: Include in judge prompt (style matching)**

```python
JUDGE_PROMPT = """
You are evaluating whether the response matches the target writing style.

## Reference Examples (this is what good looks like)
{reference_examples}

## Rubric
Rate how well the response matches the style of the reference examples:
- Word choice and vocabulary
- Sentence structure and length
- Tone and personality
- Domain-specific patterns

## Response to Evaluate
{response}

Return JSON with scores 1-5 for each dimension.
"""
```

**Option 2: Similarity scoring**

```python
def score_style_similarity(response, reference_examples):
    """Score how similar the response is to reference examples."""
    prompt = f"""
    Compare this response to the reference examples.
    Rate similarity 1-5 where 5 means "could have been written by the same person".

    Reference examples:
    {reference_examples}

    Response to evaluate:
    {response}

    Return: {{"similarity": <1-5>, "reasoning": "<explanation>"}}
    """
    # ... call judge model
```

**Option 3: Few-shot in the optimized prompt**

Include reference examples directly in the prompt being optimized, so the model learns the target style.

### Requesting Examples from Users

> "For this style-matching optimization, I need to see what 'good' looks like.
>
> Can you share 3-5 examples of ideal outputs? For instance:
> - If impersonating someone, share messages they've actually written
> - If matching brand voice, share approved copy
> - If domain-specific, share expert-verified answers
>
> Without these, the optimizer can only make generic improvements."

## Common Pitfalls

1. **Gaming the judge** - The prompt may optimize for judge preferences rather than real quality
   - Mitigation: Use diverse scenarios, validate manually on held-out cases

2. **Rubric drift** - Changing the rubric invalidates previous scores
   - Mitigation: Lock the rubric before optimization

3. **Judge hallucination** - Judge invents scores without reasoning
   - Mitigation: Require reasoning field, validate JSON structure

4. **Overfitting to scenarios** - Prompt works for test cases but fails generally
   - Mitigation: Hold out scenarios for final validation

## Model Selection

### Judge Model Recommendations

Use capable models for judging—judge quality directly affects optimization quality.

**Recommended (in order):**
1. **Claude Opus** - Highest evaluation fidelity, best reasoning stability
2. **GPT-4.1 / Claude Sonnet** - Good balance of quality and cost
3. **LLaMA-3.1-70B** - Cost-effective for large-scale runs

**Execution model** (running the prompt being optimized) can be cheaper—Sonnet or Haiku usually suffice.

```python
# Recommended configuration
JUDGE_MODEL = "claude-opus-4-6"      # High quality for judging
EXECUTION_MODEL = "claude-sonnet-4-5"  # Faster/cheaper for execution
```

### Multi-Judge Ensemble

For reduced variance on high-stakes optimization, use multiple judges and average:

```python
JUDGE_MODELS = [
    "claude-opus-4-6",
    "gpt-4.1",
]

def ensemble_judge(scenario, response):
    """Average scores across multiple judge models."""
    scores = []
    for model in JUDGE_MODELS:
        judgment = judge_response(scenario, response, model=model)
        scores.append(judgment["overall"])
    return sum(scores) / len(scores)

def judge_response(scenario, response, model):
    """Judge with a specific model."""
    client = Anthropic() if "claude" in model else OpenAI()
    # ... implementation
```

Ensemble judging roughly doubles cost but significantly reduces score variance.

## Weighted Dimensions

If some dimensions matter more than others, use weighted aggregation:

```python
def aggregate_scores(judgment, weights=None):
    """Aggregate dimension scores with optional weighting."""
    scores = judgment["scores"]

    if weights is None:
        # Equal weights
        return sum(scores.values()) / len(scores)

    # Weighted average
    total = sum(scores[dim] * weight for dim, weight in weights.items())
    return total / sum(weights.values())

# Example: Accuracy matters twice as much as other dimensions
DIMENSION_WEIGHTS = {
    "clarity": 1.0,
    "accuracy": 2.0,
    "grounding": 2.0,
    "helpfulness": 1.0,
}

overall = aggregate_scores(judgment, DIMENSION_WEIGHTS)
```

**Important:** Decide weights before optimization and keep them fixed. Changing weights mid-optimization invalidates comparisons.

## Held-Out Validation

---

**⚠️ REQUIRED GATE: This is not optional ⚠️**

You MUST split scenarios into training and held-out sets before optimization. Do not skip this step. Without held-out validation, you cannot distinguish real improvement from overfitting.

---

Always reserve scenarios for final validation. This catches overfitting to the training scenarios.

### Splitting Scenarios

```python
import random

def split_scenarios(scenarios, holdout_ratio=0.2, seed=42):
    """Split scenarios into training and held-out sets."""
    random.seed(seed)
    shuffled = scenarios.copy()
    random.shuffle(shuffled)

    split_idx = int(len(shuffled) * (1 - holdout_ratio))
    return {
        "training": shuffled[:split_idx],
        "holdout": shuffled[split_idx:],
    }

# Usage
splits = split_scenarios(ALL_SCENARIOS, holdout_ratio=0.2)
TRAINING_SCENARIOS = splits["training"]  # Used during optimization
HOLDOUT_SCENARIOS = splits["holdout"]    # Used only for final validation
```

### Held-Out Validation

After optimization, run a single evaluation on held-out scenarios and compare against the baseline:

```python
"""validate_holdout.py - Validate on held-out scenarios."""
import math
from pathlib import Path


def run_single_evaluation(prompt, scenarios):
    """Run one complete evaluation across all scenarios."""
    total = 0
    for scenario in scenarios:
        response = run_with_prompt(prompt, scenario)
        judgment = judge_response(scenario, response)
        total += judgment["overall"]
    return total / len(scenarios)


def validate_holdout(baseline_stats, optimized_path, scenarios):
    """Validate optimized prompt on held-out scenarios.

    Args:
        baseline_stats: Dict with 'mean', 'std_dev', 'n_runs' from measure_baseline()
        optimized_path: Path to optimized prompt
        scenarios: Held-out scenarios
    """
    optimized = Path(optimized_path).read_text()

    baseline_mean = baseline_stats["mean"]
    std_dev = baseline_stats["std_dev"]
    n_baseline = baseline_stats["n_runs"]

    # Single evaluation on held-out
    print("Running held-out evaluation...")
    score = run_single_evaluation(optimized, scenarios)
    print(f"  Score: {score:.2f}")

    # SE of difference: accounts for uncertainty in baseline mean (N runs)
    # and single optimized eval (1 run)
    se_diff = std_dev * math.sqrt(1/n_baseline + 1)
    threshold = 2 * se_diff

    improvement = score - baseline_mean
    significant = improvement > threshold

    print(f"  Improvement: {improvement:+.2f}")
    print(f"  Threshold (2xSE): {threshold:.2f}")
    print(f"  Significant: {significant}")

    status = "NO_IMPROVEMENT" if improvement <= 0 else (
        "SIGNIFICANT" if significant else "NOT_SIGNIFICANT"
    )

    return {
        "status": status,
        "baseline_mean": baseline_mean,
        "optimized_score": score,
        "improvement": improvement,
        "threshold": threshold,
        "significant": significant,
    }
```

### Understanding the SE Threshold

The threshold `2 x SE_diff` accounts for uncertainty in both measurements:

```
SE_diff = std_dev x sqrt(1/N_baseline + 1/N_optimized)
```

| Baseline runs | Optimized runs | SE_diff (x std_dev) | Threshold (x std_dev) |
|---------------|----------------|---------------------|----------------------|
| 3 | 1 | 1.15 | 2.31 |
| 5 | 1 | 1.10 | 2.19 |

The baseline runs establish variance. Each subsequent evaluation (optimization steps and held-out validation) uses a single run.

### Interpreting Results

| Status | Meaning | Action |
|--------|---------|--------|
| NO_IMPROVEMENT | Optimized scored lower than baseline | Reject |
| NOT_SIGNIFICANT | Improvement within noise | Reject |
| SIGNIFICANT | Improvement > 2xSE | Accept |

## evaluate.sh

Wrapper script for weco. Sources `.env` for API keys, activates virtual environments, and runs evaluation:

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

python evaluate.py
```

## Environment Pre-flight

**Before the first evaluation run**, complete the environment pre-flight checklist described in SKILL.md:

1. **Detect package manager** — `uv`, `pip`, `npm`, `cargo`, etc.
2. **Create isolated environment** — `.weco/<task>/.venv` for Python
3. **Install dependencies** — `pip install anthropic python-dotenv` (or equivalent)
4. **Verify `.env` is accessible** — `test -r .env` (never read contents)
5. **Dry-run** — `bash .weco/<task>/evaluate.sh` — fix any errors before proceeding

Do not proceed to baseline measurement or optimization until the dry-run passes.

## Full Workflow

```bash
# 1. Setup
mkdir -p .weco/task
cp prompt.txt .weco/task/optimize.txt
cp prompt.txt .weco/task/baseline.txt

# 2. Environment pre-flight
cd .weco/task
python -m venv .venv && source .venv/bin/activate
pip install anthropic python-dotenv
test -r ../../.env && echo ".env: OK"
cd ../..

# 3. Dry-run evaluation
bash .weco/task/evaluate.sh
# Fix any errors before proceeding

# 4. Measure baseline (ask user: 3 or 5 runs?)
python measure_baseline.py .weco/task/baseline.txt
# Output: mean=3.7, std_dev=0.15, n_runs=5

# 5. Run optimization (single evaluation per step)
weco run \
  --source .weco/task/optimize.txt \
  --eval-command "bash .weco/task/evaluate.sh" \
  --metric prompt_quality \
  --goal maximize \
  --steps 10 \
  --apply-change

# 6. Validate on held-out (single eval)
python validate_holdout.py
# Output:
#   Score: 4.1, improvement: +0.4, threshold: 0.33 -> SIGNIFICANT

# 7. Accept and apply
cp .weco/task/optimize.txt prompt.txt
```

