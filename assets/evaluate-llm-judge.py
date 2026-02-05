"""Evaluate prompt quality using LLM-as-judge.

This runs a single evaluation. Weco calls this once per optimization step.
Statistical rigor is handled separately:
1. Baseline variance measurement (before optimization) - see measure_baseline.py
2. Progressive held-out validation (after optimization) - see validate_holdout.py

IMPORTANT: Weco optimizes a SINGLE metric. This script prints exactly one
metric in the format: metric_name: value (e.g., "prompt_quality: 4.25")

IMPORTANT: ANTHROPIC_API_KEY must be available via .env file or environment
variable. The agent must never read, check, or handle API keys directly.

IMPORTANT: Run the environment pre-flight before first use:
1. Create a venv: python -m venv .venv && source .venv/bin/activate
2. Install deps: pip install anthropic python-dotenv
3. Verify .env: test -r .env (or ../../.env)
4. Dry-run: bash evaluate.sh
See SKILL.md "Environment Pre-flight" for the full checklist.
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

# =============================================================================
# CONFIGURATION
# =============================================================================

# Model for executing the prompt being optimized
EXECUTION_MODEL = "claude-sonnet-4-5"

# Model for judging responses (use a capable model)
JUDGE_MODEL = "claude-sonnet-4-5"

# All models used in this script (for validation)
ALL_MODELS = list(set([EXECUTION_MODEL, JUDGE_MODEL]))


# =============================================================================
# MODEL VALIDATION
# =============================================================================

def validate_models():
    """Smoke test that all configured models are available on this API key."""
    from anthropic import Anthropic
    client = Anthropic()
    all_ok = True
    for model_id in ALL_MODELS:
        try:
            client.messages.create(
                model=model_id,
                max_tokens=1,
                messages=[{"role": "user", "content": "hi"}],
            )
            print(f"  ok: {model_id}", file=sys.stderr)
        except Exception as e:
            print(f"  FAILED: {model_id} - {e}", file=sys.stderr)
            all_ok = False
    return all_ok


# =============================================================================
# LOAD THE ARTIFACT BEING OPTIMIZED
# =============================================================================

# Resolve paths relative to this script's directory, not the working directory.
# This works whether the script lives at .weco/prompt-optimization/evaluate.py
# or any other location — it always looks for optimize.txt alongside itself.
SCRIPT_DIR = Path(__file__).parent

def load_artifact(path):
    with open(path) as f:
        return f.read()


# The prompt/skill being optimized (same directory as this script)
optimized = load_artifact(SCRIPT_DIR / "optimize.txt")


# =============================================================================
# TRAINING SCENARIOS - Used during optimization
# =============================================================================
# Reserve ~20% of scenarios as held-out for final validation (in scenarios.py).
# Each scenario should have:
# - input: The user request or context
# - expected_behaviors: List of behaviors the response should exhibit
#
# Cover: common cases, edge cases, failure modes, boundary conditions

TRAINING_SCENARIOS = [
    {
        "input": "TODO: Replace with actual user request",
        "expected_behaviors": [
            "TODO: Expected behavior 1",
            "TODO: Expected behavior 2",
        ],
    },
    # TODO: Add diverse scenarios
    #
    # Example for an agent skill:
    # {
    #     "input": "Optimize this sorting function for speed",
    #     "expected_behaviors": [
    #         "asks which mode the user prefers",
    #         "measures baseline performance",
    #         "runs weco with correct flags",
    #         "asks before applying changes",
    #     ],
    # },
    #
    # Example for a system prompt:
    # {
    #     "input": "What's the weather like?",
    #     "expected_behaviors": [
    #         "stays in character",
    #         "politely declines out-of-scope requests",
    #         "suggests appropriate alternatives",
    #     ],
    # },
]


# =============================================================================
# JUDGE PROMPT - Define your evaluation rubric
# =============================================================================
# Customize the dimensions to match what matters for your artifact.
# Each dimension should be independent and measurable.

JUDGE_PROMPT = """
You are evaluating a prompt's effectiveness based on the response it produced.

## Rubric

Rate each dimension 1-5:

1. **Clarity** (1-5): Is the response clear and unambiguous?
   - 5: Crystal clear, no room for misinterpretation
   - 3: Mostly clear with minor ambiguities
   - 1: Confusing or contradictory

2. **Completeness** (1-5): Does it address all aspects of the request?
   - 5: Fully addresses everything asked
   - 3: Addresses main points, misses some details
   - 1: Incomplete or ignores key aspects

3. **Correctness** (1-5): Is the information/behavior accurate?
   - 5: Fully accurate and appropriate
   - 3: Mostly correct with minor issues
   - 1: Contains significant errors

4. **Helpfulness** (1-5): Does it effectively help the user?
   - 5: Exceptionally helpful, anticipates needs
   - 3: Adequately helpful
   - 1: Not helpful or counterproductive

## Expected Behaviors

The response should exhibit these behaviors:
{expected_behaviors}

Check each expected behavior and factor into your scores.

## Output Format

Return ONLY valid JSON (no markdown, no explanation outside JSON):
{{
  "reasoning": "<brief explanation of your scoring>",
  "scores": {{
    "clarity": <1-5>,
    "completeness": <1-5>,
    "correctness": <1-5>,
    "helpfulness": <1-5>
  }},
  "behaviors_exhibited": ["<list behaviors from expected that were present>"],
  "overall": <1-5>
}}
"""


# =============================================================================
# EXECUTION AND JUDGING FUNCTIONS
# =============================================================================

def run_with_prompt(prompt: str, scenario: dict) -> str:
    """Execute the prompt being optimized against a scenario."""
    # Using Anthropic - replace with OpenAI if preferred
    from anthropic import Anthropic

    client = Anthropic()
    response = client.messages.create(
        model=EXECUTION_MODEL,
        max_tokens=2048,
        system=prompt,
        messages=[{"role": "user", "content": scenario["input"]}],
    )
    return response.content[0].text


def judge_response(scenario: dict, response: str) -> dict:
    """Have a capable LLM judge the response quality."""
    from anthropic import Anthropic

    client = Anthropic()

    judge_input = JUDGE_PROMPT.format(
        expected_behaviors="\n".join(f"- {b}" for b in scenario["expected_behaviors"])
    )

    result = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"{judge_input}\n\n## Response to Evaluate\n\n{response}"
        }],
    )

    # Parse JSON response
    try:
        return json.loads(result.content[0].text)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse judge response: {e}")
        print(f"Raw response: {result.content[0].text}")
        # Return neutral score on parse failure
        return {"overall": 3.0, "reasoning": "Parse error"}


# =============================================================================
# MAIN EVALUATION LOOP
# =============================================================================

if __name__ == "__main__":
    if not TRAINING_SCENARIOS or "TODO" in str(TRAINING_SCENARIOS[0]):
        print("Error: TRAINING_SCENARIOS not configured. Edit this file.")
        print("prompt_quality: 0.00")
        exit(1)

    # Validate models before running any scenarios
    print("Validating model availability...", file=sys.stderr)
    if not validate_models():
        print("Error: One or more models are not available. Fix the model "
              "configuration at the top of this file.", file=sys.stderr)
        print("prompt_quality: 0.00")
        exit(1)

    total_score = 0.0
    scenario_count = 0

    for i, scenario in enumerate(TRAINING_SCENARIOS):
        try:
            # Execute the prompt
            response = run_with_prompt(optimized, scenario)

            # Judge the response
            judgment = judge_response(scenario, response)
            score = judgment["overall"]

            total_score += score
            scenario_count += 1

            print(f"Scenario {i+1}/{len(TRAINING_SCENARIOS)}: {score:.2f}/5")

        except Exception as e:
            print(f"Error in scenario {i+1}: {e}")
            total_score += 1.0  # Penalize failures
            scenario_count += 1

    # Final metric for Weco
    avg_score = total_score / scenario_count if scenario_count > 0 else 0.0
    print(f"prompt_quality: {avg_score:.2f}")
