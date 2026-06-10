---
name: setup
description: Install and authenticate Weco CLI
metadata:
  tags: install, login, authentication, credits
---

## Check if Weco is installed

```bash
which weco
```

## Check authentication

```bash
weco credits balance
```

If this succeeds, Weco is ready to use.

If authentication fails, run `weco login` directly rather than asking the user to run it in a separate terminal.

## Install Weco CLI

If not installed:

```bash
pipx install weco
```

## Authenticate

Login via browser (opens authentication page):

```bash
weco login
```

To logout:

```bash
weco logout
```

## Credit Management

```bash
weco credits balance     # Check current balance
weco credits topup       # Purchase additional credits
weco credits autotopup   # Configure automatic top-up
```

## Using Your Own API Keys

You can provide your own LLM API keys instead of using Weco credits:

```bash
weco run ... --api-key openai=YOUR_KEY anthropic=YOUR_KEY gemini=YOUR_KEY
```

Supported providers:
- `gemini` (default model: `gemini-3-flash-preview`)
- `openai` (default model: `o4-mini`)
- `anthropic` (default model: `claude-opus-4-5`)
