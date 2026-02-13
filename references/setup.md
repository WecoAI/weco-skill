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

## Install Weco CLI

If not installed, use the official installer:

```bash
curl -fsSL https://weco.ai/install.sh | sh
```

On Windows (PowerShell):

```powershell
irm https://weco.ai/install.ps1 | iex
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
- `openai` (default model: `o4-mini`)
- `anthropic` (default model: `claude-opus-4-5`)
- `gemini` (default model: `gemini-3-pro-preview`)
