"""Evaluate skill quality via multi-turn conversations and transcript grading.

This runs a single evaluation. Weco calls this once per optimization step.
Statistical rigor is handled separately:
1. Baseline variance measurement (before optimization) - see measure_baseline()
2. Progressive held-out validation (after optimization) - see validate_holdout.py

IMPORTANT: Weco optimizes a SINGLE metric. This script prints exactly one
metric in the format: metric_name: value (e.g., "skill_quality: 4.25")

IMPORTANT: API key (ANTHROPIC_API_KEY or OPENAI_API_KEY) must be available
via .env file or environment variable. The agent must never read, check,
or handle API keys directly.

IMPORTANT: Run the environment pre-flight before first use:
1. Create a venv: python -m venv .venv && source .venv/bin/activate
2. Install deps: pip install anthropic python-dotenv  (or: pip install openai python-dotenv)
3. Verify .env: test -r .env (or ../../.env)
4. Dry-run: bash evaluate.sh
See SKILL.md "Environment Pre-flight" for the full checklist.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Load API keys from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# =============================================================================
# PROVIDER CONFIGURATION — set to "anthropic" or "openai"
# =============================================================================

PROVIDER = "anthropic"

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================
# Anthropic: claude-sonnet-4-5, claude-haiku-4-5, claude-opus-4-6
# OpenAI:    gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, o3

# Model for running the skill (the "agent under test")
SKILL_MODEL = "claude-sonnet-4-5"

# Model for the user simulator (cheaper model is fine)
SIMULATOR_MODEL = "claude-haiku-4-5"

# Model for checking if user input is needed (cheap, fast)
INPUT_CHECK_MODEL = "claude-haiku-4-5"

# Model for grading transcripts (use a capable model)
JUDGE_MODEL = "claude-sonnet-4-5"

# Maximum conversation turns per scenario
MAX_TURNS = 10

# All models used in this script (for validation)
ALL_MODELS = list(set([SKILL_MODEL, SIMULATOR_MODEL, INPUT_CHECK_MODEL, JUDGE_MODEL]))


# =============================================================================
# PROVIDER ABSTRACTION
# =============================================================================

def chat(model, messages, system=None, max_tokens=1024):
    """Send a chat request to the configured provider."""
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


# =============================================================================
# MODEL VALIDATION
# =============================================================================

def validate_models():
    """Smoke test that all configured models are available."""
    all_ok = True
    for model_id in ALL_MODELS:
        try:
            chat(model_id, [{"role": "user", "content": "hi"}], max_tokens=1)
            print(f"  ok: {model_id}", file=sys.stderr)
        except Exception as e:
            print(f"  FAILED: {model_id} - {e}", file=sys.stderr)
            all_ok = False
    return all_ok


# =============================================================================
# LOAD THE ARTIFACT BEING OPTIMIZED
# =============================================================================

# Resolve paths relative to this script's directory, not the working directory.
# This works whether the script lives at .weco/skill-optimization/evaluate.py
# or any other location — it always looks for optimize.md alongside itself.
SCRIPT_DIR = Path(__file__).parent

def load_artifact(path):
    with open(path) as f:
        return f.read()


# The skill being optimized (same directory as this script)
optimized = load_artifact(SCRIPT_DIR / "optimize.md")


# =============================================================================
# REFERENCES (optional - included in system prompt alongside the skill)
# =============================================================================

def build_system_prompt(skill_content, references_dir=None):
    """Build system prompt from skill content and optional references."""
    system = skill_content

    if references_dir and Path(references_dir).exists():
        ref_content = []
        for ref_file in sorted(Path(references_dir).glob("*.md")):
            ref_content.append(
                f"\n\n---\n## Reference: {ref_file.stem}\n\n{ref_file.read_text()}"
            )
        if ref_content:
            system += "\n\n# References" + "".join(ref_content)

    return system


# Path to references directory (set to None if no references)
REFERENCES_DIR = SCRIPT_DIR / "references" if (SCRIPT_DIR / "references").exists() else None


# =============================================================================
# TRAINING SCENARIOS - Used during optimization
# =============================================================================
# Reserve ~20% of scenarios as held-out for final validation.
# Each scenario should have:
# - name: Identifier for the scenario
# - initial_message: What the user asks initially
# - context_files: (optional) Files to include in the first message
# - user_simulator_instructions: How the simulated user should behave
# - expected_behaviors: List of behaviors the skill should exhibit
#
# Cover: happy path, edge cases, clarification needed, constraint tests

TRAINING_SCENARIOS = [
    {
        "name": "TODO_scenario_name",
        "initial_message": "TODO: Replace with actual user request",
        "context_files": {
            # "example.py": "def foo(): return 42"
        },
        "user_simulator_instructions": """TODO: How the simulated user should behave:
- When asked X, respond with Y
- Approve reasonable suggestions
""",
        "expected_behaviors": [
            "TODO: Expected behavior 1",
            "TODO: Expected behavior 2",
        ],
    },
    # TODO: Add diverse scenarios
    #
    # Example for a code optimization skill:
    # {
    #     "name": "typical_optimization",
    #     "initial_message": "Optimize this sorting function for speed",
    #     "context_files": {
    #         "sort.py": "def sort(arr):\n    return sorted(arr)"
    #     },
    #     "user_simulator_instructions": """
    #     - When asked which mode, say "Vibe Mode"
    #     - When asked about constraints, say "no external dependencies"
    #     - Approve suggestions that seem reasonable
    #     """,
    #     "expected_behaviors": [
    #         "Asks which mode the user prefers",
    #         "Measures baseline performance",
    #         "Asks before applying changes",
    #     ],
    # },
]


# =============================================================================
# MULTI-TURN CONVERSATION HARNESS
# =============================================================================

def run_scenario(skill_content, scenario, max_turns=MAX_TURNS):
    """Run a single multi-turn scenario and return the transcript."""
    system_prompt = build_system_prompt(skill_content, REFERENCES_DIR)

    # Build the initial user message, including context files if any
    initial_content = scenario["initial_message"]
    if scenario.get("context_files"):
        files_context = "\n\n".join(
            f"File: `{name}`\n```\n{content}\n```"
            for name, content in scenario["context_files"].items()
        )
        initial_content = f"{files_context}\n\n{initial_content}"

    # Start conversation
    messages = [{"role": "user", "content": initial_content}]

    assistant_msg = chat(SKILL_MODEL, messages, system=system_prompt, max_tokens=4096)
    messages.append({"role": "assistant", "content": assistant_msg})

    transcript = [
        {"role": "user", "content": scenario["initial_message"]},
        {"role": "assistant", "content": assistant_msg},
    ]

    # Continue until done or max turns
    turns = 1
    while turns < max_turns and needs_user_input(transcript):
        user_reply = simulate_user(transcript, scenario["user_simulator_instructions"])

        messages.append({"role": "user", "content": user_reply})

        assistant_msg = chat(SKILL_MODEL, messages, system=system_prompt, max_tokens=4096)
        messages.append({"role": "assistant", "content": assistant_msg})

        transcript.append({"role": "user", "content": user_reply})
        transcript.append({"role": "assistant", "content": assistant_msg})
        turns += 1

    return transcript


def needs_user_input(transcript):
    """Use an LLM to judge whether the conversation needs user input.

    Returns True if the assistant is waiting for a response, False if done.
    """
    transcript_text = format_transcript(transcript)

    response = chat(
        INPUT_CHECK_MODEL,
        [{"role": "user", "content": f"""Analyze this conversation between a user and an AI assistant.

Determine if the assistant is:
1. WAITING for user input (asked a question, requested confirmation, needs information)
2. DONE (task complete, or assistant is working autonomously without needing input)

Conversation:
{transcript_text}

Reply with exactly one word: WAITING or DONE"""}],
        max_tokens=16,
    )

    return "WAITING" in response


# =============================================================================
# USER SIMULATOR
# =============================================================================

def simulate_user(transcript, instructions):
    """Generate a simulated user response."""
    transcript_text = format_transcript(transcript)

    return chat(
        SIMULATOR_MODEL,
        [{"role": "user", "content": f"""You are simulating a user interacting with an AI assistant.

Instructions for how to behave:
{instructions}

The conversation so far:
{transcript_text}

Generate the next user response. Be concise and natural. Output ONLY the response, nothing else."""}],
        max_tokens=512,
    )


# =============================================================================
# TRANSCRIPT GRADER
# =============================================================================

GRADER_PROMPT = """Evaluate this conversation transcript against expected behaviors.

EXPECTED BEHAVIORS:
{behaviors_list}

TRANSCRIPT:
{transcript_text}

For each expected behavior, determine if it occurred in the transcript.
Then provide an overall score from 1-5:
- 5: All behaviors occurred correctly
- 4: Most behaviors occurred, minor issues
- 3: Some behaviors occurred, some missing
- 2: Few behaviors occurred, major issues
- 1: Behaviors did not occur or were incorrect

Output your analysis as JSON:
{{
  "reasoning": "<brief explanation>",
  "behavior_results": [
    {{"behavior": "<behavior text>", "present": true/false, "evidence": "<quote or explanation>"}}
  ],
  "overall": <1-5>
}}"""


def grade_transcript(transcript, expected_behaviors):
    """Grade a transcript against expected behaviors. Returns 1-5."""
    behaviors_list = "\n".join(f"- {b}" for b in expected_behaviors)
    transcript_text = format_transcript(transcript)

    text = chat(
        JUDGE_MODEL,
        [{"role": "user", "content": GRADER_PROMPT.format(
            behaviors_list=behaviors_list,
            transcript_text=transcript_text,
        )}],
        max_tokens=1024,
    )

    # Try JSON parsing first
    try:
        result = json.loads(text)
        return result.get("overall", 3)
    except json.JSONDecodeError:
        pass

    # Fallback: look for SCORE: X pattern
    for line in reversed(text.split("\n")):
        line = line.strip()
        if line.startswith("SCORE:"):
            try:
                return int(line.split(":")[1].strip())
            except (ValueError, IndexError):
                pass

    # Last resort fallback
    return 3


# =============================================================================
# HELPERS
# =============================================================================

def format_transcript(transcript):
    return "\n\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in transcript
    )


def save_transcript(transcript, scenario_name, score, transcripts_dir):
    """Save transcript to file for debugging and review."""
    transcripts_dir = Path(transcripts_dir)
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{scenario_name}_score{score}.json"

    transcript_data = {
        "scenario": scenario_name,
        "score": score,
        "timestamp": timestamp,
        "transcript": transcript
    }

    (transcripts_dir / filename).write_text(
        json.dumps(transcript_data, indent=2)
    )
    return filename


# =============================================================================
# MAIN EVALUATION LOOP
# =============================================================================

if __name__ == "__main__":
    if not TRAINING_SCENARIOS or "TODO" in str(TRAINING_SCENARIOS[0].get("name", "")):
        print("Error: TRAINING_SCENARIOS not configured. Edit this file.")
        print("skill_quality: 0.00")
        exit(1)

    # Validate models before running any scenarios
    print("Validating model availability...", file=sys.stderr)
    if not validate_models():
        print("Error: One or more models are not available. Fix the model "
              "configuration at the top of this file.", file=sys.stderr)
        print("skill_quality: 0.00")
        exit(1)

    transcripts_dir = SCRIPT_DIR / "transcripts"

    total_score = 0.0
    scenario_count = 0

    for i, scenario in enumerate(TRAINING_SCENARIOS):
        try:
            print(f"Running scenario: {scenario['name']}", file=sys.stderr)

            # Run multi-turn conversation
            transcript = run_scenario(optimized, scenario)

            # Grade the transcript
            score = grade_transcript(transcript, scenario["expected_behaviors"])

            # Save for debugging
            filename = save_transcript(
                transcript, scenario["name"], score, transcripts_dir
            )
            print(f"  Score: {score}/5 (saved: {filename})", file=sys.stderr)

            total_score += score
            scenario_count += 1

        except Exception as e:
            print(f"  Error in scenario {scenario['name']}: {e}", file=sys.stderr)
            total_score += 1.0  # Penalize failures
            scenario_count += 1

    # Final metric for Weco
    avg_score = total_score / scenario_count if scenario_count > 0 else 0.0
    print(f"skill_quality: {avg_score:.2f}")
