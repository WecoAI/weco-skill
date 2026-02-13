# Weco AI Skill

AI-powered code optimization skill for Claude Code and Cursor.

## What is this?

This skill teaches your AI coding assistant how to use [Weco](https://weco.ai) for code optimization. When you ask to "make this faster" or "improve accuracy", the assistant will:

1. Analyze your code and environment
2. Set up an evaluation benchmark
3. Run Weco's optimization engine
4. Present results with a detailed report
5. Apply changes (with your approval)

## Installation

### Recommended: Weco CLI

The easiest way to install is via the [Weco CLI](https://weco.ai/docs/cli), which sets up the skill and trigger rules for your agent:

```bash
pip install weco
weco install cursor   # For Cursor
weco install claude   # For Claude Code
```

### Quick install: npx

Install the skill using the Agent Skills CLI:

```bash
npx skills add weco-ai/weco-skill
```

This installs the skill directory (SKILL.md, CLAUDE.md, references, assets). For Cursor, this relies on the skill description for activation — for the always-on trigger rule, use `weco install cursor` instead.

### Manual install: install.sh

```bash
./install.sh
```

The installer will ask which AI assistant you use (Claude Code, Cursor, or both) and set up the skill with trigger rules accordingly.

### What Gets Installed

**Claude Code:**
```
~/.claude/skills/weco/
├── CLAUDE.md          # Trigger snippet (Claude reads this)
├── SKILL.md           # Full optimization workflow
├── references/        # Advanced documentation
│   ├── benchmarking.md
│   ├── ml-evaluation.md
│   └── ...
└── assets/            # Template evaluation scripts
    ├── evaluate-speed.py
    ├── evaluate-accuracy.py
    └── ...
```

**Cursor (via `weco install cursor` or `install.sh`):**
```
~/.cursor/
├── rules/
│   └── weco.mdc           # Always-on trigger rule
└── skills/
    └── weco/
        ├── SKILL.md       # Full optimization workflow
        ├── references/    # Advanced documentation
        └── assets/        # Template evaluation scripts
```

## Usage

Once installed, just ask your AI assistant to optimize code:

- "Make this function faster"
- "Optimize this for speed"
- "Improve the accuracy of this model"
- "Reduce the latency"

The skill offers two modes:

- **Vibe Mode**: Minimal questions, maximum action. Great for simple optimizations.
- **Assistant Scientist Mode**: Collaborative, educational. Best for complex cases or learning.

## Requirements

- [Weco CLI](https://weco.ai/docs/cli) installed and authenticated
- Claude Code or Cursor

## Files

```
weco-skill/
├── SKILL.md              # Full skill instructions (source of truth)
├── CLAUDE.md             # Trigger snippet for Claude Code (ships with skill)
├── install.sh            # Interactive installer
├── README.md             # This file
├── snippets/             # Trigger snippets (used by weco-cli installer)
│   ├── claude.md         # Claude Code trigger
│   ├── claude-global.md  # Claude Code global trigger
│   └── cursor.md         # Cursor trigger (.mdc rule)
├── references/           # Advanced documentation
│   ├── benchmarking.md
│   ├── ml-evaluation.md
│   ├── gpu-profiling.md
│   └── ...
└── assets/               # Template evaluation scripts
    ├── evaluate-speed.py
    ├── evaluate-accuracy.py
    └── ...
```

## Learn More

- [Weco Documentation](https://weco.ai/docs)
- [Claude Code](https://claude.ai/code)
- [Cursor](https://cursor.sh)
