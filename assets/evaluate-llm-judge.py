"""Evaluate prompt/skill quality using LLM-as-judge.

IMPORTANT: Weco optimizes a SINGLE metric. This script should print exactly one
metric in the format: metric_name: value (e.g., "prompt_quality: 4.25")

This template evaluates natural language artifacts (prompts, skills, templates)
by having an LLM judge the quality of responses they produce.

API KEYS: This script reads API keys from environment variables automatically.
Set ANTHROPIC_API_KEY and/or OPENAI_API_KEY before running:
    export ANTHROPIC_API_KEY='your-key-here'
"""
import json
import os

# =============================================================================
# CONFIGURATION - Adjust these for your use case
# =============================================================================

# Number of times to run each scenario (reduces variance)
RUNS_PER_SCENARIO = 1  # Increase to 2-3 for more stable results

# Model for executing the prompt being optimized
# Anthropic models require ANTHROPIC_API_KEY env var
# OpenAI models require OPENAI_API_KEY env var
EXECUTION_MODEL = "claude-sonnet-4-20250514"

# Model for judging responses (use a capable model)
JUDGE_MODEL = "claude-sonnet-4-20250514"


# =============================================================================
# LOAD THE ARTIFACT BEING OPTIMIZED
# =============================================================================

def load_artifact(path):
    with open(path) as f:
        return f.read()


# The prompt/skill being optimized
optimized = load_artifact(".weco/optimize.txt")


# =============================================================================
# TEST SCENARIOS - Define 10-20 diverse test cases
# =============================================================================
# Each scenario should have:
# - input: The user request or context
# - expected_behaviors: List of behaviors the response should exhibit
#
# Cover: common cases, edge cases, failure modes, boundary conditions

TEST_SCENARIOS = [
    {
        "input": "TODO: Replace with actual user request",
        "expected_behaviors": [
            "TODO: Expected behavior 1",
            "TODO: Expected behavior 2",
        ],
    },
    # TODO: Add 10-20 diverse scenarios
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
    if not TEST_SCENARIOS or "TODO" in str(TEST_SCENARIOS[0]):
        print("Error: TEST_SCENARIOS not configured. Edit evaluate-llm-judge.py")
        print("prompt_quality: 0.00")
        exit(1)

    total_score = 0.0
    scenario_count = 0

    for i, scenario in enumerate(TEST_SCENARIOS):
        scenario_scores = []

        for run in range(RUNS_PER_SCENARIO):
            try:
                # Execute the prompt
                response = run_with_prompt(optimized, scenario)

                # Judge the response
                judgment = judge_response(scenario, response)
                scenario_scores.append(judgment["overall"])

                # Optional: Print progress
                if RUNS_PER_SCENARIO > 1:
                    print(f"Scenario {i+1}, run {run+1}: {judgment['overall']}/5")

            except Exception as e:
                print(f"Error in scenario {i+1}, run {run+1}: {e}")
                scenario_scores.append(1.0)  # Penalize failures

        # Average scores for this scenario
        avg_scenario_score = sum(scenario_scores) / len(scenario_scores)
        total_score += avg_scenario_score
        scenario_count += 1

        print(f"Scenario {i+1}/{len(TEST_SCENARIOS)}: {avg_scenario_score:.2f}/5")

    # Final metric
    avg_score = total_score / scenario_count if scenario_count > 0 else 0.0
    print(f"prompt_quality: {avg_score:.2f}")
