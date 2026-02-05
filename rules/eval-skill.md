---
name: eval-skill
description: Evaluate Claude Code skills by running multi-turn conversations and grading transcripts
metadata:
  tags: skill, claude-code, agent, evaluation, transcript
---

## When to Use

Use skill evaluation when optimizing:
- Claude Code skills (SKILL.md files)
- Cursor skills
- Agent system prompts
- Multi-turn conversational workflows
- Any artifact that guides agent behavior

## How It Works

1. **Analyze the skill** - Understand what behaviors it should produce
2. **Generate test scenarios** - Create realistic user interactions
3. **Run conversations** - Execute the skill as a system prompt via API, simulating multi-turn interactions
4. **Grade transcripts** - Use an LLM judge to evaluate if expected behaviors occurred
5. **Aggregate scores** - Average across scenarios for final metric

## Critical Requirements

### API Key Requirements

Skill evaluation requires `ANTHROPIC_API_KEY` for conversations, simulation, and grading.

**The agent must NEVER read, check, display, or handle API keys in any way.** Do not run commands like `echo $ANTHROPIC_API_KEY`, `env | grep KEY`, `printenv`, or read `.env` file contents. Do not ask users to paste keys into the chat.

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

### Skill as System Prompt

The skill content is passed directly as the system prompt in API calls. This simulates how skills work in practice - they're loaded as instructions that guide the agent's behavior.

```python
from anthropic import Anthropic

client = Anthropic()

# The skill IS the system prompt
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=4096,
    system=skill_content,
    messages=[{"role": "user", "content": "User's request"}]
)
```

### Multi-Turn Conversations

Multi-turn conversations use message accumulation. Each turn appends to the messages list:

```python
messages = []

# Turn 1
messages.append({"role": "user", "content": "Initial request"})
response = client.messages.create(
    model=MODEL, max_tokens=4096,
    system=skill_content, messages=messages
)
messages.append({"role": "assistant", "content": response.content[0].text})

# Turn 2 (simulated user reply)
messages.append({"role": "user", "content": simulated_reply})
response = client.messages.create(
    model=MODEL, max_tokens=4096,
    system=skill_content, messages=messages
)
messages.append({"role": "assistant", "content": response.content[0].text})
```

### Including Rules

Skills often reference rules in a `rules/` directory. Include rule content in the system prompt alongside the skill so the model can reference it during evaluation:

```python
def build_system_prompt(skill_content, rules_dir=None):
    """Build system prompt from skill content and optional rules."""
    system = skill_content

    if rules_dir and Path(rules_dir).exists():
        rules_content = []
        for rule_file in sorted(Path(rules_dir).glob("*.md")):
            rules_content.append(
                f"\n\n---\n## Rule: {rule_file.stem}\n\n{rule_file.read_text()}"
            )
        if rules_content:
            system += "\n\n# Referenced Rules" + "".join(rules_content)

    return system
```

**Important:** Only the skill file (`optimize.md`) is optimized. Rules are reference material included in the system prompt, but they are not modified by Weco.

### Output Format

Print the final score in weco format:

```
skill_quality: 4.25
```

## Handling Skills with Rules

Copy rules so they're available during evaluation:

```bash
# Copy the skill (this is what Weco will optimize)
cp SKILL.md .weco/task/optimize.md
cp SKILL.md .weco/task/baseline.md

# Copy rules so they're included in the system prompt during evaluation
cp -r rules/ .weco/task/rules/
```

### Full Workflow

```bash
# 1. Setup
mkdir -p .weco/task
cp SKILL.md .weco/task/optimize.md
cp SKILL.md .weco/task/baseline.md
cp -r rules/ .weco/task/rules/

# 2. Run weco optimization (only optimizes optimize.md)
weco run --source .weco/task/optimize.md --eval-command "bash .weco/task/evaluate.sh" --metric skill_quality --goal maximize

# 3. Apply changes back
cp .weco/task/optimize.md SKILL.md
```

## Template

See [assets/evaluate-skill.py](../assets/evaluate-skill.py) for a consolidated single-file template that includes all components (harness, simulator, grader) ready to customize.

## Complete Harness

### Directory Structure

```
.weco/<task>/
  optimize.md          # Skill being optimized (weco modifies this)
  baseline.md          # Original skill (reference)
  rules/               # Rules included in system prompt (not optimized)
  evaluate.py          # Main evaluation script
  harness.py           # Multi-turn conversation runner
  simulator.py         # User response simulation
  grader.py            # Transcript grading
  scenarios.py         # Test scenario definitions
  evaluate.sh          # Wrapper script
```

### scenarios.py

Define test scenarios that exercise the skill's behaviors. The number of scenarios should scale with skill complexity (see "Generating Scenarios from a Skill" below).

```python
"""Test scenarios for skill evaluation.

Scenario count is determined by skill complexity:
- Simple skill (3-4 behaviors): 5-6 scenarios
- Medium skill (5-8 behaviors): 7-10 scenarios
- Complex skill (9+ behaviors): 10-15 scenarios

Reserve ~20% for held-out validation.
"""

SCENARIOS = [
    {
        "name": "scenario_name",
        "initial_message": "What the user asks initially",
        "context_files": {
            # Files referenced in the scenario (included in first message)
            "example.py": "def foo(): return 42"
        },
        "user_simulator_instructions": """How the simulated user should behave:
- When asked X, respond with Y
- Approve reasonable suggestions
- Provide requested information
""",
        "expected_behaviors": [
            "Specific behavior the skill should exhibit",
            "Another expected behavior",
            "Asks before making changes",
        ]
    },
    # Add scenarios to cover:
    # - Happy path (typical usage) - always include
    # - Clarification needed (vague requests)
    # - Edge cases (unusual but valid inputs)
    # - Constraint tests (verify limits are respected)
    # - Different user personas (if applicable)
    # - Error handling (if skill uses external systems)
]
```

### Configuration

Use model aliases (not dated snapshot IDs) so scripts stay current. See the Model Reference in SKILL.md for the full list.

```python
"""Model configuration for skill evaluation."""

# Model for running the skill (the "agent under test")
SKILL_MODEL = "claude-sonnet-4-5"

# Model for the user simulator
SIMULATOR_MODEL = "claude-haiku-4-5"

# Model for grading transcripts (use a capable model)
JUDGE_MODEL = "claude-sonnet-4-5"

# Maximum turns per scenario
MAX_TURNS = 10
```

### Model Validation

**Before running any evaluation**, validate that the configured models are available. Add this to `evaluate.py` and call it before running scenarios:

```python
def validate_models(client, *model_ids):
    """Smoke test model availability. Call before running evaluation."""
    all_ok = True
    for model_id in model_ids:
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
```

If a model fails, stop immediately and report which model is unavailable. Suggest an alternative from the Model Reference.

### harness.py

Runs multi-turn conversations with the skill loaded as system prompt.

**Important:** The harness uses an LLM (`needs_user_input()`) to judge whether each turn requires user input or if the task is complete. This enables realistic multi-turn evaluation without hardcoding conversation length.

```python
"""Multi-turn conversation harness for skill evaluation."""
from pathlib import Path
from anthropic import Anthropic


# Model configuration
SKILL_MODEL = "claude-sonnet-4-5"
INPUT_CHECK_MODEL = "claude-haiku-4-5"


def build_system_prompt(skill_content, rules_dir=None):
    """Build system prompt from skill content and optional rules."""
    system = skill_content

    if rules_dir and Path(rules_dir).exists():
        rules_content = []
        for rule_file in sorted(Path(rules_dir).glob("*.md")):
            rules_content.append(
                f"\n\n---\n## Rule: {rule_file.stem}\n\n{rule_file.read_text()}"
            )
        if rules_content:
            system += "\n\n# Referenced Rules" + "".join(rules_content)

    return system


def run_scenario(skill_content, scenario, user_simulator, max_turns=10, rules_dir=None):
    """Run a single scenario and return the transcript.

    Args:
        skill_content: The main skill content (SKILL.md)
        scenario: Scenario definition with initial_message, context_files, etc.
        user_simulator: UserSimulator instance
        max_turns: Maximum conversation turns
        rules_dir: Optional path to rules/ directory. If provided, rules are
                   included in the system prompt alongside the skill.
    """
    client = Anthropic()
    system_prompt = build_system_prompt(skill_content, rules_dir)

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

    response = client.messages.create(
        model=SKILL_MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
    )
    assistant_msg = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_msg})

    transcript = [
        {"role": "user", "content": scenario["initial_message"]},
        {"role": "assistant", "content": assistant_msg},
    ]

    # Continue until done or max turns
    turns = 1
    while turns < max_turns and needs_user_input(transcript):
        user_reply = user_simulator.respond(
            transcript,
            scenario["user_simulator_instructions"]
        )

        messages.append({"role": "user", "content": user_reply})

        response = client.messages.create(
            model=SKILL_MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
        )
        assistant_msg = response.content[0].text
        messages.append({"role": "assistant", "content": assistant_msg})

        transcript.append({"role": "user", "content": user_reply})
        transcript.append({"role": "assistant", "content": assistant_msg})
        turns += 1

    return transcript


def needs_user_input(transcript):
    """Use an LLM to judge whether the conversation needs user input.

    Analyzes the transcript and determines:
    - WAITING: Assistant asked a question or is waiting for user response
    - DONE: Task is complete, or assistant is working without needing input

    Returns True if user input is needed, False otherwise.
    """
    client = Anthropic()
    transcript_text = format_transcript(transcript)

    response = client.messages.create(
        model=INPUT_CHECK_MODEL,
        max_tokens=16,
        messages=[{
            "role": "user",
            "content": f"""Analyze this conversation between a user and an AI assistant.

Determine if the assistant is:
1. WAITING for user input (asked a question, requested confirmation, needs information)
2. DONE (task complete, or assistant is working autonomously without needing input)

Conversation:
{transcript_text}

Reply with exactly one word: WAITING or DONE"""
        }],
    )

    return "WAITING" in response.content[0].text


def format_transcript(transcript):
    return "\n\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in transcript
    )
```

### simulator.py

Generates realistic user responses using the API:

```python
"""User simulator for multi-turn conversations."""
from anthropic import Anthropic


SIMULATOR_MODEL = "claude-haiku-4-5"


class UserSimulator:
    def respond(self, transcript, instructions):
        """Generate a user response."""
        client = Anthropic()
        transcript_text = self._format_transcript(transcript)

        response = client.messages.create(
            model=SIMULATOR_MODEL,
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": f"""You are simulating a user interacting with an AI assistant.

Instructions for how to behave:
{instructions}

The conversation so far:
{transcript_text}

Generate the next user response. Be concise and natural. Output ONLY the response, nothing else."""
            }],
        )

        return response.content[0].text

    def _format_transcript(self, transcript):
        return "\n\n".join(
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in transcript
        )
```

### grader.py

Evaluates transcripts against expected behaviors:

```python
"""Transcript grader for skill evaluation."""
import json
from anthropic import Anthropic


JUDGE_MODEL = "claude-sonnet-4-5"


def grade_transcript(transcript, expected_behaviors):
    """Grade a transcript against expected behaviors. Returns 1-5."""
    client = Anthropic()

    behaviors_list = "\n".join(f"- {b}" for b in expected_behaviors)
    transcript_text = "\n\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in transcript
    )

    response = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Evaluate this conversation transcript against expected behaviors.

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
        }],
    )

    text = response.content[0].text

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
```

### evaluate.py

Main orchestrator that Weco invokes. Runs a **single evaluation** per step.

```python
"""Skill evaluation - run scenarios and grade transcripts.

This runs a single evaluation. Weco calls this once per optimization step.
Statistical rigor is handled by:
1. Baseline variance measurement (before optimization)
2. Progressive held-out validation (after optimization)

IMPORTANT: ANTHROPIC_API_KEY must be available via .env file or environment
variable. The agent must never read, check, or handle API keys directly.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# Load API keys from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from anthropic import Anthropic
from harness import run_scenario, SKILL_MODEL, INPUT_CHECK_MODEL
from simulator import UserSimulator, SIMULATOR_MODEL
from grader import grade_transcript, JUDGE_MODEL
from scenarios import TRAINING_SCENARIOS  # Only training scenarios during optimization


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


def main():
    # Default: look for optimize.md in the same directory as this script
    default_path = Path(__file__).parent / "optimize.md"
    skill_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path
    skill_content = skill_path.read_text()

    # Validate models before running scenarios
    print("Validating model availability...", file=sys.stderr)
    if not validate_models(
        Anthropic(), SKILL_MODEL, SIMULATOR_MODEL, INPUT_CHECK_MODEL, JUDGE_MODEL
    ):
        print("Error: One or more models unavailable. Fix model config.", file=sys.stderr)
        print("skill_quality: 0.00")
        sys.exit(1)

    # Check for rules directory alongside the skill
    rules_dir = skill_path.parent / "rules"
    if not rules_dir.exists():
        rules_dir = None

    transcripts_dir = skill_path.parent / "transcripts"
    simulator = UserSimulator()
    scores = []

    for scenario in TRAINING_SCENARIOS:
        print(f"Running scenario: {scenario['name']}", file=sys.stderr)

        try:
            transcript = run_scenario(
                skill_content, scenario, simulator,
                rules_dir=rules_dir
            )
            score = grade_transcript(transcript, scenario["expected_behaviors"])

            filename = save_transcript(
                transcript, scenario["name"], score, transcripts_dir
            )
            print(f"  Score: {score}/5 (saved: {filename})", file=sys.stderr)

            scores.append(score)
        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)
            scores.append(1)  # Treat errors as failures

    avg_score = sum(scores) / len(scores) if scores else 0

    # Single score output for Weco
    print(f"skill_quality: {avg_score:.2f}")


if __name__ == "__main__":
    main()
```

### Transcript Format

Transcripts are saved as JSON files in `.weco/<task>/transcripts/`:

```
transcripts/
  20240115_143022_typical_usage_score4.json
  20240115_143045_edge_case_score3.json
  20240115_143112_error_handling_score5.json
```

Each file contains:
```json
{
  "scenario": "typical_usage",
  "score": 4,
  "timestamp": "20240115_143022",
  "transcript": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    ...
  ]
}
```

Review transcripts to understand why scenarios scored low and iterate on the skill.

### evaluate.sh

Wrapper script for weco. Sources `.env` for API keys, activates virtual environments, and runs evaluation consistently across Claude Code, Cursor, and standalone execution:

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

### Environment Pre-flight

**Before the first evaluation run**, complete the environment pre-flight checklist described in SKILL.md. This is a required step that prevents cascading setup failures:

1. **Detect package manager** — `uv`, `pip`, `npm`, `cargo`, etc.
2. **Create isolated environment** — `.weco/<task>/.venv` for Python
3. **Install dependencies** — `pip install anthropic python-dotenv` (or equivalent)
4. **Verify `.env` is accessible** — `test -r .env` (never read contents)
5. **Dry-run** — `bash .weco/<task>/evaluate.sh` — fix any errors before proceeding

Do not proceed to baseline measurement or optimization until the dry-run passes.

## Generating Scenarios from a Skill

When optimizing an arbitrary skill, analyze it to generate scenarios that **discriminate between good and bad skill versions**. The goal is not just coverage — it's creating scenarios where a better skill measurably outperforms a worse one.

### Step 1: Understand the Skill

Read the skill and identify:
- **Purpose**: What does this skill help users do?
- **Triggers**: What user requests activate this skill?
- **Key behaviors**: What should happen in a conversation?
- **Decision points**: Where does the skill ask for user input?
- **Constraints**: What should the skill NOT do?

Then identify:
- **Weaknesses**: Where are the instructions vague, incomplete, or ambiguous? Where might the skill produce inconsistent behavior?
- **Underspecified areas**: What situations does the skill not explicitly address? What happens when the user does something unexpected?
- **Quality gradients**: Where could the skill do a task adequately vs. excellently? (e.g., "explains what changed" could be a one-liner or a thorough analysis)

#### Tool Dependency Check (Required)

**Before designing scenarios**, check whether the skill relies heavily on tool execution. Look for:

- References to specific scripts or functions (e.g., `summarize_csv()`, `analyze.py`)
- Instructions that assume file system access (reading/writing files, listing directories)
- Workflows that depend on command execution (running scripts, installing packages)
- References to tool calls, MCP servers, or external APIs

**If the skill is tool-dependent**, warn the user before proceeding:

> "This skill relies on [specific tool/script] for core functionality. The API-based evaluation can test conversational behavior (workflow, communication, decision-making) but **cannot execute actual tools**.
>
> Options:
> 1. **Behavioral optimization only** — Evaluate whether the skill describes the right actions, asks the right questions, and follows the right workflow. This works well for improving communication quality and workflow adherence.
> 2. **Add tool definitions to the harness** — Include tool schemas in the API call so the model produces structured tool_use blocks instead of just describing actions. More realistic but more complex to set up.
> 3. **Split optimization** — Optimize the skill's conversational behavior here, and separately optimize the tool code (e.g., `analyze.py`) using standard Weco code optimization.
>
> Which approach would you prefer?"

**Do not build the full evaluation harness before resolving this.** Discovering tool limitations after creating scenarios and running the baseline wastes significant time and API credits.

For behavioral-only evaluation, adjust expected behaviors to test intent rather than execution:

```python
# Instead of testing actual execution:
# "Successfully runs analyze.py and produces output"

# Test behavioral intent:
expected_behaviors = [
    "Describes running analyze.py with the correct arguments",
    "Explains what the analysis will produce before running it",
    "Asks user for confirmation before executing the script",
]
```

### Step 2: Determine Scenario Count and Difficulty Mix

The number of scenarios should scale with skill complexity:

| Factor | How to Count |
|--------|--------------|
| Distinct behaviors | Count explicit "should do X" instructions |
| User personas | Count different user types mentioned or implied |
| Decision branches | Count places where skill behavior varies based on input |
| Constraints | Count "should NOT" or limitation instructions |
| Weak spots | Count vague/incomplete instructions |

**Guidelines:**
- **Minimum**: 5 scenarios (floor for meaningful signal)
- **Simple skill** (3-4 behaviors): 5-6 scenarios
- **Medium skill** (5-8 behaviors): 7-10 scenarios
- **Complex skill** (9+ behaviors, rules files): 10-15 scenarios

Reserve ~20% of scenarios for held-out validation.

---

**⚠️ REQUIRED: Difficulty gradient and failure-targeting ⚠️**

Scenarios MUST include a mix of difficulties. If every scenario tests the same basic thing, the evaluation cannot distinguish between skill versions — the model aces all scenarios trivially and the optimizer has no signal to improve on.

**Required distribution:**

| Difficulty | % of Scenarios | Purpose |
|------------|----------------|---------|
| Easy (sanity checks) | ~30% | Verify basic functionality works. Should score 4-5/5 on baseline. |
| Medium (nuanced) | ~40% | Test quality of execution, not just correctness. Should score 3-4/5 on baseline. |
| Hard (stress tests) | ~30% | Target weaknesses, vague instructions, edge cases. Should score 2-3/5 on baseline. |

**At least 2 scenarios MUST target areas where the current skill is likely to fail or score poorly.** To create these:
1. Read the skill and find instructions that are vague or incomplete
2. Find situations the skill doesn't explicitly address
3. Create scenarios that exercise those gaps

If the baseline scores 4.5+ on all scenarios, the scenarios are too easy and need to be replaced with harder ones.

---

### Step 3: Generate Scenarios

For each scenario, assign both a **category** and a **difficulty level**:

| Scenario Type | What to Test | Difficulty |
|---------------|--------------|------------|
| Happy path | Typical usage with cooperative user | Easy |
| Clarification needed | Vague request requiring questions | Easy-Medium |
| Quality of output | How well it explains, adapts, communicates | Medium |
| Different personas | Novice vs expert users | Medium |
| Multi-step workflow | Complex task requiring multiple turns | Medium-Hard |
| Constraint test | Verify the skill respects limits | Medium-Hard |
| Weakness targeting | Scenarios exploiting vague/incomplete instructions | Hard |
| Edge case | Unusual but valid inputs | Hard |
| Error handling | How the skill handles problems | Hard |

### Designing Discriminating Expected Behaviors

Expected behaviors should test **quality**, not just **presence**. Instead of binary "did it or didn't it" checks, include behaviors that require judgment about how well something was done:

```python
# Bad - binary, easy to ace trivially
expected_behaviors = [
    "Analyzes the code",
    "Provides output",
]

# Good - tests quality and depth
expected_behaviors = [
    "Identifies at least 2 specific performance bottlenecks (not generic advice)",
    "Explains WHY each bottleneck matters with quantitative reasoning",
    "Adapts explanation depth to the user's apparent expertise level",
    "Suggests actionable fixes, not just observations",
]

# Good - tests behavior under ambiguity
expected_behaviors = [
    "Asks clarifying questions rather than assuming",
    "Handles the contradictory requirements gracefully",
    "Explains the tradeoff between the conflicting goals",
]
```

**Quality dimensions to consider for expected behaviors:**
- **Insight quality**: Does it identify non-obvious issues, not just surface-level ones?
- **Adaptation quality**: Does it adjust to the user's expertise, context, constraints?
- **Communication quality**: Is the explanation clear, structured, appropriately detailed?
- **Judgment quality**: When instructions are vague, does it make reasonable decisions?

### Step 4: Present Scenarios for User Verification

**Before writing the evaluation harness, present your proposed scenarios to the user for review.**

Format your proposal like this:

> Based on my analysis of the skill, I've identified these scenarios for evaluation:
>
> **Skill Complexity:** Medium (6 distinct behaviors, 2 constraints)
> **Identified Weaknesses:** [list vague/underspecified areas]
> **Proposed Scenarios:** 8 total (6 training + 2 held-out)
>
> | # | Name | Difficulty | Type | What It Tests |
> |---|------|------------|------|---------------|
> | 1 | typical_request | Easy | Happy path | Basic usage with clear request |
> | 2 | expert_user | Easy | Persona | Sanity check: adapts to technical user |
> | 3 | quality_of_explanation | Medium | Quality | Depth and clarity of explanations |
> | 4 | multi_step_task | Medium | Workflow | Handles complex multi-turn task |
> | 5 | persona_adaptation | Medium | Quality | Adapts tone/detail to user expertise |
> | 6 | vague_instructions_gap | Hard | Weakness | Skill doesn't specify how to handle X |
> | 7 | contradictory_request | Hard | Edge case | Conflicting user requirements |
> | 8 | constraint_boundary | Hard | Constraint | Pushes limits of what skill should refuse |
>
> **Why the hard scenarios matter:**
> - Scenario 6 targets [specific vague area in the skill]
> - Scenario 7 tests judgment when instructions don't cover this case
>
> **Expected behaviors per scenario:**
> - Scenario 1: [list key behaviors]
> - ...
>
> Do these scenarios provide good coverage? Would you like to add, remove, or modify any?

Wait for user confirmation before proceeding.

### Step 5: Define Expected Behaviors

Extract expected behaviors from the skill's instructions:

```python
# From skill text like:
# "Always ask before making changes to files"

expected_behaviors = [
    "Asks for confirmation before editing files",
    "Does not modify files without approval",
]
```

### Step 6: Create User Simulator Instructions

Based on the scenario, define how the simulated user should respond:

```python
user_simulator_instructions = """
- When asked about preferences, choose option A
- Approve reasonable suggestions
- When asked for clarification, provide specific details
- If asked about file paths, provide realistic paths
"""
```

## Limitations

### No Tool Execution

The API-based evaluation runs the skill as a system prompt without tool access. The model describes what it *would* do (read files, run commands, etc.) rather than actually executing tools.

This works well for evaluating:
- Conversational behavior (asking questions, explaining, confirming)
- Workflow adherence (following the right steps in the right order)
- Constraint compliance (respecting limits, not doing forbidden things)
- Communication quality (tone, clarity, helpfulness)

This is less suited for evaluating:
- Actual tool call correctness (exact arguments, proper sequencing)
- File system interactions (reading/writing specific files)
- Command execution (running specific shell commands)

For most skill optimization, behavioral evaluation is sufficient since skills primarily guide *what* the agent does and *how* it communicates, not the exact tool call syntax.

### External Services

If the skill references external commands or APIs, the model will describe invoking them without actually running them. The grader evaluates whether the model *describes* the correct behavior:

```python
# The grader checks behavioral intent, not execution
expected_behaviors = [
    "Describes running weco with the correct flags",
    "Mentions checking for existing evaluation scripts",
    "Says it will back up the original file",
]
```

## Statistical Rigor

Skill evaluation has high variance from multiple sources: model non-determinism, user simulator responses, and transcript grading. You must account for this before optimization.

### Sources of Variance

| Source | Impact | Mitigation |
|--------|--------|------------|
| Model non-determinism | High | Multiple evaluation runs |
| User simulator variation | Medium | Consistent simulator instructions |
| Transcript grading | Medium | Structured grading rubric |
| Scenario-level luck | Low | More scenarios |

### Variance Estimation (Required Before Optimization)

---

**⚠️ REQUIRED GATE: This is not optional ⚠️**

You MUST measure baseline variance before running optimization. Do not skip this step. Without variance measurement, you cannot know whether optimization results are real improvements or noise.

---

Run the baseline evaluation multiple times before optimizing:

| Runs | Confidence | Recommendation |
|------|------------|----------------|
| 3 | Acceptable | Recommended default |
| 5 | Good | For high-stakes optimization |

Ask the user how many baseline runs to perform (minimum 3).

```python
"""Measure baseline stability before optimization."""
import statistics
import math
from pathlib import Path
from harness import run_scenario
from simulator import UserSimulator
from grader import grade_transcript
from scenarios import TRAINING_SCENARIOS

def measure_baseline(skill_path, scenarios, runs=3):
    """Measure baseline mean and variance.

    Args:
        runs: Number of full evaluation runs. Minimum 3.
    """
    if runs < 3:
        raise ValueError("Need at least 3 runs for reliable std dev")

    skill_content = Path(skill_path).read_text()
    rules_dir = Path(skill_path).parent / "rules"
    if not rules_dir.exists():
        rules_dir = None

    simulator = UserSimulator()

    run_scores = []
    for run_idx in range(runs):
        print(f"Baseline run {run_idx + 1}/{runs}...")

        scenario_scores = []
        for scenario in scenarios:
            transcript = run_scenario(
                skill_content, scenario, simulator,
                rules_dir=rules_dir
            )
            score = grade_transcript(transcript, scenario["expected_behaviors"])
            scenario_scores.append(score)

        run_avg = sum(scenario_scores) / len(scenario_scores)
        run_scores.append(run_avg)
        print(f"  Run {run_idx + 1} average: {run_avg:.2f}")

    mean = statistics.mean(run_scores)
    std_dev = statistics.stdev(run_scores)
    std_err = std_dev / math.sqrt(runs)

    return {
        "mean": mean,
        "scores": run_scores,
        "std_dev": std_dev,
        "std_err": std_err,
        "n_runs": runs,
    }

# Example output:
# {"mean": 3.5, "scores": [3.3, 3.6, 3.6], "std_dev": 0.17, "std_err": 0.10, "n_runs": 3}
```

### Interpreting Baseline Variance

| Std Dev | Quality | Recommendation |
|---------|---------|----------------|
| < 0.2 | Good | Proceed with optimization |
| 0.2 - 0.4 | Acceptable | Proceed with caution |
| > 0.4 | High | Simplify scenarios or improve grading rubric first |

If variance is high (> 0.4), **warn the user and suggest fixes before proceeding.** Do not proceed without user acknowledgment. Suggest:
- Making expected_behaviors more specific and measurable
- Simplifying user_simulator_instructions for consistency
- Reducing max_turns to limit conversation divergence
- Adding more scenarios for a more stable signal

### Held-Out Scenarios (Required)

---

**⚠️ REQUIRED GATE: This is not optional ⚠️**

You MUST split scenarios into training and held-out sets before optimization. Do not skip this step. Without held-out validation, you cannot distinguish real improvement from overfitting.

---

Reserve ~20% of scenarios for final validation. This catches overfitting to training scenarios.

```python
"""Split scenarios into training and held-out sets."""
import random

def split_scenarios(scenarios, holdout_ratio=0.2, seed=42):
    """Split scenarios for training and validation."""
    random.seed(seed)
    shuffled = scenarios.copy()
    random.shuffle(shuffled)

    split_idx = int(len(shuffled) * (1 - holdout_ratio))
    return {
        "training": shuffled[:split_idx],
        "holdout": shuffled[split_idx:],
    }

# In scenarios.py:
ALL_SCENARIOS = [...]  # All scenarios (count depends on skill complexity)

splits = split_scenarios(ALL_SCENARIOS, holdout_ratio=0.2)
TRAINING_SCENARIOS = splits["training"]  # Used during optimization
HOLDOUT_SCENARIOS = splits["holdout"]    # Used only for final validation
```

Examples:
- 6 scenarios -> 5 training, 1 held-out
- 10 scenarios -> 8 training, 2 held-out
- 15 scenarios -> 12 training, 3 held-out

### Held-Out Validation

After optimization, run a single evaluation on held-out scenarios and compare against the baseline:

```python
"""validate_holdout.py - Validate on held-out scenarios."""
import math
from pathlib import Path
from harness import run_scenario
from simulator import UserSimulator
from grader import grade_transcript
from scenarios import HOLDOUT_SCENARIOS


def run_single_evaluation(skill_content, scenarios, simulator, rules_dir=None):
    """Run one complete evaluation across all scenarios."""
    scores = []
    for scenario in scenarios:
        transcript = run_scenario(
            skill_content, scenario, simulator,
            rules_dir=rules_dir
        )
        score = grade_transcript(transcript, scenario["expected_behaviors"])
        scores.append(score)
    return sum(scores) / len(scores)


def validate_holdout(baseline_stats, optimized_path, scenarios):
    """Validate optimized skill on held-out scenarios.

    Args:
        baseline_stats: Dict with 'mean', 'std_dev', 'n_runs' from measure_baseline()
        optimized_path: Path to optimized skill
        scenarios: Held-out scenarios
    """
    skill_content = Path(optimized_path).read_text()
    rules_dir = Path(optimized_path).parent / "rules"
    if not rules_dir.exists():
        rules_dir = None

    simulator = UserSimulator()

    baseline_mean = baseline_stats["mean"]
    std_dev = baseline_stats["std_dev"]
    n_baseline = baseline_stats["n_runs"]

    # Single evaluation on held-out
    print("Running held-out evaluation...")
    score = run_single_evaluation(
        skill_content, scenarios, simulator, rules_dir=rules_dir
    )
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


# Usage:
# baseline_stats = measure_baseline(".weco/task/baseline.md", HOLDOUT_SCENARIOS, runs=3)
# result = validate_holdout(baseline_stats, ".weco/task/optimize.md", HOLDOUT_SCENARIOS)
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

### Full Workflow

```bash
# 1. Setup
mkdir -p .weco/task
cp SKILL.md .weco/task/optimize.md
cp SKILL.md .weco/task/baseline.md
cp -r rules/ .weco/task/rules/

# 2. Measure baseline (ask user: 3 or 5 runs?)
python measure_baseline.py .weco/task/baseline.md
# Output: mean=3.5, std_dev=0.17, n_runs=3

# 3. Run optimization (single evaluation per step)
weco run \
  --source .weco/task/optimize.md \
  --eval-command "bash .weco/task/evaluate.sh" \
  --metric skill_quality \
  --goal maximize \
  --steps 10 \
  --apply-change

# 4. Validate on held-out (single eval)
python validate_holdout.py
# Output:
#   Score: 3.9, improvement: +0.4, threshold: 0.39 -> SIGNIFICANT

# 5. Accept and apply
cp .weco/task/optimize.md SKILL.md
```

### Interpreting Results

| Status | Meaning | Action |
|--------|---------|--------|
| NO_IMPROVEMENT | Optimized scored lower than baseline | Reject |
| NOT_SIGNIFICANT | Improvement within noise | Reject |
| SIGNIFICANT | Improvement > 2xSE | Accept |

## Running the Optimization

```bash
weco run \
  --source .weco/task/optimize.md \
  --eval-command "bash .weco/task/evaluate.sh" \
  --metric skill_quality \
  --goal maximize \
  --steps 10 \
  --apply-change
```

## Evaluation Structure

Each scenario evaluation involves:
- Multi-turn API calls (2-10 per scenario)
- User simulation calls (1 per turn)
- Grading call (1 per scenario)

### Full Optimization Breakdown

| Phase | Purpose |
|-------|---------|
| Baseline variance measurement | Establish std dev before optimization |
| Optimization steps | Each step runs multiple evaluations |
| Held-out validation | Final validation on reserved scenarios |
