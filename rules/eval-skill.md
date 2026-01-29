---
name: eval-skill
description: Evaluate Claude Code skills by running multi-turn conversations and grading transcripts
metadata:
  tags: skill, claude-code, agent, evaluation, transcript
---

## When to Use

Use skill evaluation when optimizing:
- Claude Code skills (SKILL.md files)
- Agent system prompts
- Multi-turn conversational workflows
- Any artifact that guides Claude Code behavior

## How It Works

1. **Analyze the skill** - Understand what behaviors it should produce
2. **Generate test scenarios** - Create realistic user interactions
3. **Run conversations** - Execute Claude Code sessions with the skill loaded
4. **Grade transcripts** - Use Claude to evaluate if expected behaviors occurred
5. **Aggregate scores** - Average across scenarios for final metric

## Critical Requirements

### Skill Loading

Write the skill to `.claude/skills/SKILL.md` in the working directory:

```python
from pathlib import Path

def install_skill(skill_content, work_dir):
    skill_dir = Path(work_dir) / ".claude" / "skills"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(skill_content)
```

### Multi-Turn Sessions

Use `claude -p` with `--resume` for multi-turn conversations:

```bash
# Start session
session_id=$(claude -p "Initial message" --output-format json | jq -r '.session_id')

# Continue session
claude -p "Follow-up message" --resume "$session_id" --output-format json
```

### Output Format

Print the final score in weco format:

```
skill_quality: 4.25
```

## Handling Skills with Rules

Skills often have associated rules in a `rules/` directory. Copy them so Claude can reference them during evaluation:

```bash
# Copy the skill (this is what Weco will optimize)
cp SKILL.md .weco/task/optimize.md
cp SKILL.md .weco/task/baseline.md

# Copy rules so Claude can reference them during evaluation
cp -r rules/ .weco/task/rules/
```

During evaluation, Claude reads rules on-demand via tool calls (matching real usage). This keeps the system prompt small and tests realistic behavior.

**Important:** Only the skill file (`optimize.md`) is optimized. Rules are reference material that Claude can read during scenarios, but they are not modified by Weco.

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

## Complete Harness

### Directory Structure

```
.weco/<task>/
  optimize.md          # Skill being optimized (weco modifies this)
  baseline.md          # Original skill (reference)
  rules/               # Rules copied for Claude to reference (not optimized)
  evaluate.py          # Main evaluation script
  harness.py           # Claude Code invocation
  simulator.py         # User response simulation
  grader.py            # Transcript grading
  scenarios.py         # Test scenario definitions
  evaluate.sh          # Wrapper script
```

### scenarios.py

Define test scenarios that exercise the skill's behaviors:

```python
"""Test scenarios for skill evaluation."""

SCENARIOS = [
    {
        "name": "scenario_name",
        "initial_message": "What the user asks initially",
        "context_files": {
            # Files that should exist in the test environment
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
    # Add 3-5 scenarios covering:
    # - Happy path (typical usage)
    # - Edge cases (unusual inputs)
    # - Different user types/personas
]
```

### harness.py

Runs Claude Code sessions and captures transcripts:

```python
"""Claude Code session harness for skill evaluation."""
import subprocess
import json
import tempfile
import os
import stat
import shutil
from pathlib import Path


def run_scenario(skill_content, scenario, user_simulator, max_turns=10, rules_dir=None):
    """Run a single scenario and return the transcript.

    Args:
        skill_content: The main skill content (SKILL.md)
        scenario: Scenario definition with initial_message, context_files, etc.
        user_simulator: UserSimulator instance
        max_turns: Maximum conversation turns
        rules_dir: Optional path to rules/ directory. If provided, rules are
                   copied to the temp dir so Claude can read them on-demand.
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Install skill (just the main skill, not rules)
        skill_dir = tmpdir / ".claude" / "skills"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(skill_content)

        # Copy rules directory if provided (Claude reads on-demand)
        if rules_dir and Path(rules_dir).exists():
            shutil.copytree(rules_dir, tmpdir / "rules")

        # Set up mock files for this scenario
        for filename, content in scenario.get("context_files", {}).items():
            filepath = tmpdir / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)

        # Set up any mock commands (optional)
        setup_mocks(tmpdir)

        # Prepare environment
        env = os.environ.copy()
        env["PATH"] = str(tmpdir) + ":" + env["PATH"]

        # Start session
        result = subprocess.run(
            ["claude", "-p", scenario["initial_message"], "--output-format", "json"],
            capture_output=True, text=True, cwd=tmpdir, env=env
        )
        response = json.loads(result.stdout)
        session_id = response["session_id"]

        transcript = [
            {"role": "user", "content": scenario["initial_message"]},
            {"role": "assistant", "content": response["result"]}
        ]

        # Continue until done or max turns
        turns = 1
        while turns < max_turns and needs_user_input(transcript):
            user_reply = user_simulator.respond(
                transcript,
                scenario["user_simulator_instructions"]
            )

            result = subprocess.run(
                ["claude", "-p", user_reply, "--resume", session_id, "--output-format", "json"],
                capture_output=True, text=True, cwd=tmpdir, env=env
            )
            response = json.loads(result.stdout)

            transcript.append({"role": "user", "content": user_reply})
            transcript.append({"role": "assistant", "content": response["result"]})
            turns += 1

        return transcript


def needs_user_input(transcript):
    """Use Claude to determine if waiting for user input."""
    transcript_text = format_transcript(transcript)

    prompt = f"""Look at this conversation and determine if the assistant is waiting for user input or if the task is complete/in-progress without needing input.

{transcript_text}

Reply with exactly one word: WAITING or DONE"""

    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True, text=True
    )

    response = json.loads(result.stdout)
    return "WAITING" in response["result"]


def format_transcript(transcript):
    return "\n\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in transcript
    )


def setup_mocks(tmpdir):
    """Set up mock commands in the temp directory.

    Override this to mock external commands the skill might invoke.
    Example: mock an API CLI to return simulated results.
    """
    pass
```

### simulator.py

Generates realistic user responses:

```python
"""User simulator for multi-turn conversations."""
import subprocess
import json


class UserSimulator:
    def respond(self, transcript, instructions):
        """Generate a user response using Claude."""

        transcript_text = self._format_transcript(transcript)

        prompt = f"""You are simulating a user interacting with an AI assistant.

Instructions for how to behave:
{instructions}

The conversation so far:
{transcript_text}

Generate the next user response. Be concise and natural. Output ONLY the response, nothing else."""

        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True, text=True
        )

        response = json.loads(result.stdout)
        return response["result"]

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
import subprocess
import json


def grade_transcript(transcript, expected_behaviors):
    """Grade a transcript against expected behaviors. Returns 1-5."""

    behaviors_list = "\n".join(f"- {b}" for b in expected_behaviors)
    transcript_text = "\n\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in transcript
    )

    prompt = f"""Evaluate this Claude Code transcript against expected behaviors.

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

Output your analysis, then on the final line output exactly: SCORE: X"""

    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True, text=True
    )

    response = json.loads(result.stdout)
    text = response["result"]

    # Extract score from response
    for line in reversed(text.split("\n")):
        if line.strip().startswith("SCORE:"):
            return int(line.split(":")[1].strip())

    # Fallback if parsing fails
    return 3
```

### evaluate.py

Main orchestrator that weco invokes:

```python
"""Skill evaluation - run scenarios and grade transcripts."""
import sys
import json
from pathlib import Path
from datetime import datetime

from harness import run_scenario
from simulator import UserSimulator
from grader import grade_transcript
from scenarios import SCENARIOS


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
    # Read skill content - weco provides the path
    skill_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".weco/task/optimize.md")
    skill_content = skill_path.read_text()

    # Directory for saving transcripts
    transcripts_dir = skill_path.parent / "transcripts"

    simulator = UserSimulator()
    scores = []

    for scenario in SCENARIOS:
        print(f"Running scenario: {scenario['name']}", file=sys.stderr)

        try:
            transcript = run_scenario(skill_content, scenario, simulator)
            score = grade_transcript(transcript, scenario["expected_behaviors"])

            # Save transcript for review
            filename = save_transcript(
                transcript, scenario["name"], score, transcripts_dir
            )
            print(f"  Score: {score}/5 (saved: {filename})", file=sys.stderr)

            scores.append(score)
        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)
            scores.append(1)  # Treat errors as failures

    avg_score = sum(scores) / len(scores) if scores else 0

    # Output for weco
    print(f"skill_quality: {avg_score:.2f}")

    # Summary
    print(f"\nTranscripts saved to: {transcripts_dir}", file=sys.stderr)


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

Wrapper script for weco:

```bash
#!/bin/bash
set -e
cd "$(dirname "$0")"
python evaluate.py optimize.md
```

## Generating Scenarios from a Skill

When optimizing an arbitrary skill, analyze it to generate appropriate scenarios:

### Step 1: Understand the Skill

Read the skill and identify:
- **Purpose**: What does this skill help users do?
- **Triggers**: What user requests activate this skill?
- **Key behaviors**: What should happen in a conversation?
- **Decision points**: Where does the skill ask for user input?
- **Constraints**: What should the skill NOT do?

### Step 2: Generate Scenarios

Create 3-5 scenarios covering:

| Scenario Type | What to Test |
|---------------|--------------|
| Happy path | Typical usage with cooperative user |
| Clarification needed | Vague request requiring questions |
| Edge case | Unusual but valid inputs |
| Constraint test | Verify the skill respects limits |
| Error handling | How the skill handles problems |

### Step 3: Define Expected Behaviors

Extract expected behaviors from the skill's instructions:

```python
# From skill text like:
# "Always ask before making changes to files"

expected_behaviors = [
    "Asks for confirmation before editing files",
    "Does not modify files without approval",
]
```

### Step 4: Create User Simulator Instructions

Based on the scenario, define how the simulated user should respond:

```python
user_simulator_instructions = """
- When asked about preferences, choose option A
- Approve reasonable suggestions
- When asked for clarification, provide specific details
- If asked about file paths, provide realistic paths
"""
```

## Mocking External Commands

If the skill invokes external tools, mock them to avoid side effects and ensure reproducible evaluation.

### Critical Rule: Never Fabricate Mock Data

**You cannot invent mock responses.** Incorrect mocks produce meaningless evaluation results. Mock data must come from one of these sources:

| Source | When to Use |
|--------|-------------|
| User runs command, provides output | User has access to the service |
| User describes expected response | User knows the API but can't run it now |
| You run the real command | You have access and user gives permission |
| Dry run + user clarification | Discover what's needed, then ask user |

### Identifying What to Mock

**1. Analyze the skill:**
Read the skill instructions to identify external commands, APIs, or services it references:
- CLI tools (e.g., `gh`, `docker`, `kubectl`)
- API calls (e.g., `curl`, SDK usage)
- Build tools (e.g., `npm`, `cargo`, `make`)

**2. Ask the user for real output:**
> "This skill invokes `[command]`. Can you run it and paste the output? I need real data to create an accurate mock."

**3. Or ask user to describe the response:**
> "What does a successful response from `[command]` look like? I need the structure and typical values."

**4. Or run it yourself (with permission):**
> "I can run `[command]` to capture its output for mocking. Should I proceed?"

**5. Dry run discovery:**
Run the skill once without mocks. When it fails, ask the user about the expected response:
```
Error: Command 'myapi status' not found
```
> "The skill tried to run `myapi status`. What should this return on success?"

### Creating Mocks

```python
def setup_mocks(tmpdir):
    """Mock external commands to return simulated results."""

    # Example: Mock an API CLI tool
    mock_script = '''#!/bin/bash
cat << 'EOF'
{
  "status": "success",
  "result": {
    "id": "mock-12345",
    "score": 0.85,
    "message": "Operation completed successfully"
  }
}
EOF
'''
    mock_path = tmpdir / "myapi"
    mock_path.write_text(mock_script)
    mock_path.chmod(mock_path.stat().st_mode | stat.S_IEXEC)

    # Example: Mock a build tool
    build_mock = '''#!/bin/bash
echo "Build successful"
echo "Output: dist/bundle.js (42kb)"
exit 0
'''
    build_path = tmpdir / "build-tool"
    build_path.write_text(build_mock)
    build_path.chmod(build_path.stat().st_mode | stat.S_IEXEC)
```

## Running the Optimization

```bash
weco run \
  --source .weco/task/optimize.md \
  --eval-command "bash .weco/task/evaluate.sh" \
  --metric skill_quality \
  --goal maximize \
  --steps 10
```

## Cost Considerations

Skill evaluation is expensive because each scenario involves:
- Multiple Claude Code turns (2-10 per scenario)
- User simulation calls (1 per turn)
- Grading call (1 per scenario)

With 4 scenarios × 10 weco steps:
- ~40 full scenario evaluations
- ~200+ Claude Code invocations
- Estimated cost: $20-50 depending on conversation length

To reduce cost:
- Start with fewer scenarios (2-3) during development
- Limit max_turns per scenario
- Use --steps 5 initially to validate the approach
