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

The easiest way to install is via the [Weco CLI](https://weco.ai/docs/cli), which sets up the skill and trigger rules for your agent.

**Install the CLI:**

```bash
pipx install weco
```

**Install the skill:**

```bash
weco setup cursor       # For Cursor
weco setup claude-code  # For Claude Code
```

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

**Cursor:**
```
~/.cursor/
└── skills/
    └── weco/
        ├── SKILL.md       # Full optimization workflow
        ├── references/    # Advanced documentation
        └── assets/        # Template evaluation scripts
```

## Usage

Once installed, just ask your AI assistant to optimize code:

- "Make this function faster using /weco"
- "Optimize this for speed using /weco"
- "Improve the accuracy of this model using /weco"
- "Reduce the latency using /weco"

The skill offers two modes:

- **Vibe Mode**: Minimal questions, maximum action. Great for simple optimizations.
- **Assistant Scientist Mode**: Collaborative, educational. Best for complex cases or learning.

## Requirements

- [Weco CLI](https://weco.ai/docs/cli) installed and authenticated
- Claude Code or Cursor

## Files

```
weco-skill/
├── .cursor-plugin/       # Cursor plugin manifest
│   └── plugin.json
├── SKILL.md              # Full skill instructions (source of truth)
├── CLAUDE.md             # Trigger snippet for Claude Code (ships with skill)
├── install.sh            # Interactive installer
├── README.md             # This file
├── rules/                # Cursor plugin rules
│   └── weco.mdc          # Always-on trigger rule for Cursor
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
