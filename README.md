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

```bash
./install.sh
```

The installer will ask which AI assistant you use (Claude Code, Cursor, or both) and set up the skill accordingly.

### What Gets Installed

**Claude Code:**
```
~/.claude/skills/weco/
├── CLAUDE.md          # Trigger snippet (Claude reads this)
├── SKILL.md           # Full optimization workflow
├── rules/             # Advanced documentation
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
├── rules/
│   └── weco.mdc           # Trigger snippet (Cursor reads .mdc files)
└── skills/
    └── weco/
        ├── SKILL.md       # Full optimization workflow
        ├── rules/         # Advanced documentation
        └── assets/        # Template evaluation scripts
```

### Manual Installation

**Claude Code:**
```bash
mkdir -p ~/.claude/skills/weco
cp SKILL.md snippets/claude.md ~/.claude/skills/weco/
mv ~/.claude/skills/weco/claude.md ~/.claude/skills/weco/CLAUDE.md
cp -r rules assets ~/.claude/skills/weco/
```

**Cursor:**
```bash
mkdir -p ~/.cursor/skills/weco ~/.cursor/rules
cp snippets/cursor.md ~/.cursor/rules/weco.mdc
cp SKILL.md ~/.cursor/skills/weco/
cp -r rules assets ~/.cursor/skills/weco/
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
├── install.sh            # Interactive installer
├── README.md             # This file
├── snippets/
│   ├── claude.md         # Trigger snippet for Claude Code
│   └── cursor.md         # Trigger snippet for Cursor
├── rules/                # Advanced documentation
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
