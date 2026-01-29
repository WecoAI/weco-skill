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
3. **Use diverse test scenarios** - 10-20 scenarios covering edge cases, common cases, and failure modes
4. **Reduce variance** - Multiple runs per scenario, capable judge model
5. **Never read or display API keys** - Keys come from environment variables only

## API Key Handling

LLM-as-judge requires API keys. **Never read, display, or store API keys.**

### Required Environment Variables

| Provider | Variable | Required For |
|----------|----------|--------------|
| Anthropic | `ANTHROPIC_API_KEY` | Claude models (judge or execution) |
| OpenAI | `OPENAI_API_KEY` | GPT models (judge or execution) |

### Before Running Evaluation

Prompt the user to set keys if needed:

> "Prompt optimization requires API access for LLM-as-judge. Please set these environment variables:
> ```bash
> export ANTHROPIC_API_KEY='your-key-here'
> ```
> Let me know when ready."

### In Evaluation Code

Use standard SDK initialization—they read from environment automatically:

```python
from anthropic import Anthropic
from openai import OpenAI

# These read ANTHROPIC_API_KEY and OPENAI_API_KEY automatically
anthropic_client = Anthropic()
openai_client = OpenAI()
```

**Do not:**
- Read `.env` files or config files
- Print or echo key values
- Ask users to paste keys in chat
- Write keys to any files

## Template

See [assets/evaluate-llm-judge.py](../assets/evaluate-llm-judge.py) for the complete template.

```python
"""Evaluate prompt/skill quality using LLM-as-judge."""
import json
import os
from anthropic import Anthropic  # or openai

def load_artifact(path):
    with open(path) as f:
        return f.read()

# Load the prompt/skill being optimized
optimized = load_artifact(".weco/optimize.txt")

# Test scenarios - MUST have 10-20 diverse cases
TEST_SCENARIOS = [
    {
        "input": "User request or context here",
        "expected_behaviors": ["behavior1", "behavior2"],
    },
    # TODO: Add more scenarios covering:
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
{
  "reasoning": "<brief explanation>",
  "scores": {
    "clarity": <1-5>,
    "completeness": <1-5>,
    "correctness": <1-5>,
    "helpfulness": <1-5>
  },
  "overall": <1-5>
}
"""

def run_with_prompt(prompt, scenario):
    """Execute the prompt being optimized against a scenario."""
    client = Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
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
        model="claude-sonnet-4-20250514",  # Use capable model for judging
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"{judge_input}\n\n## Response to Evaluate\n\n{response}"
        }],
    )
    return json.loads(result.content[0].text)

# Run evaluation
total_score = 0
for scenario in TEST_SCENARIOS:
    response = run_with_prompt(optimized, scenario)
    judgment = judge_response(scenario, response)
    total_score += judgment["overall"]

avg_score = total_score / len(TEST_SCENARIOS)
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

## Reducing Variance

LLM outputs are non-deterministic. To get stable metrics:

1. **Run multiple times** - Average 2-3 runs per scenario
2. **Use capable models** - Claude Opus or GPT-4o for judging
3. **More scenarios** - 15-20 scenarios provide more stable signal than 5
4. **Structured output** - JSON reduces parsing failures

```python
# Example: Multiple runs per scenario
RUNS_PER_SCENARIO = 3

for scenario in TEST_SCENARIOS:
    scenario_scores = []
    for _ in range(RUNS_PER_SCENARIO):
        response = run_with_prompt(optimized, scenario)
        judgment = judge_response(scenario, response)
        scenario_scores.append(judgment["overall"])
    total_score += sum(scenario_scores) / len(scenario_scores)
```

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

## Cost Considerations

Each Weco step runs the full evaluation:
- N scenarios × (1 execution + 1 judgment) = 2N LLM calls per step
- With 15 scenarios and 5 Weco steps = 150 LLM calls
- Estimated cost: $1-15 depending on models used

To reduce cost:
- Start with fewer scenarios during development
- Use faster/cheaper models for execution (not judging)
- Cache scenario results when prompt hasn't changed

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
JUDGE_MODEL = "claude-opus-4-20250514"      # High quality for judging
EXECUTION_MODEL = "claude-sonnet-4-20250514"  # Faster/cheaper for execution
```

### Multi-Judge Ensemble

For reduced variance on high-stakes optimization, use multiple judges and average:

```python
JUDGE_MODELS = [
    "claude-opus-4-20250514",
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

Always reserve scenarios for final validation. This catches overfitting to the training scenarios.

### Implementation

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

### Validation Script

Create a separate `validate_holdout.py` that runs after optimization:

```python
"""Validate optimized prompt on held-out scenarios."""
from pathlib import Path
from scenarios import HOLDOUT_SCENARIOS
from evaluate import run_with_prompt, judge_response

# Load optimized and baseline prompts
optimized = Path(".weco/task/optimize.txt").read_text()
baseline = Path(".weco/task/baseline.txt").read_text()

def evaluate_prompt(prompt, scenarios):
    total = 0
    for scenario in scenarios:
        response = run_with_prompt(prompt, scenario)
        judgment = judge_response(scenario, response)
        total += judgment["overall"]
    return total / len(scenarios)

baseline_score = evaluate_prompt(baseline, HOLDOUT_SCENARIOS)
optimized_score = evaluate_prompt(optimized, HOLDOUT_SCENARIOS)

improvement = (optimized_score - baseline_score) / baseline_score * 100

print(f"Held-out baseline: {baseline_score:.2f}")
print(f"Held-out optimized: {optimized_score:.2f}")
print(f"Held-out improvement: {improvement:+.1f}%")

# Output for logging
print(f"holdout_quality: {optimized_score:.2f}")
```

### Interpreting Results

| Training Δ | Held-out Δ | Interpretation |
|------------|------------|----------------|
| +30% | +25% | Good generalization |
| +30% | +10% | Likely overfitting—consider more diverse scenarios |
| +30% | -5% | Definite overfitting—reject optimization |
| +5% | +5% | Marginal improvement—may not be worth the change |

## Cost Estimation

### Per-Step Cost

```
cost_per_step = num_scenarios × (execution_cost + judge_cost)
```

Example with 12 scenarios:
- Execution (Sonnet): 12 × $0.003 = $0.036
- Judging (Opus): 12 × $0.015 = $0.18
- **Per step: ~$0.22**

### Full Optimization

```
total_cost = cost_per_step × num_steps + holdout_validation_cost
```

Example with 10 steps + 3 holdout scenarios:
- Optimization: $0.22 × 10 = $2.20
- Holdout validation: 3 × 2 × $0.009 = $0.05 (baseline + optimized)
- **Total: ~$2.25**

### Cost Reduction Strategies

1. **Fewer scenarios during development** - Start with 6-8, expand once approach is validated
2. **Cheaper execution model** - Use Haiku for execution, keep Opus for judging
3. **Fewer steps initially** - Use `--steps 5` to validate, then run full optimization
4. **Cache baseline** - Don't re-run baseline scenarios if prompt hasn't changed
