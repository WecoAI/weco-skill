# Environment Variables and API Keys in Generated Code

When generating scripts that require API keys or other environment variables (e.g., evaluation scripts that call the Anthropic or OpenAI API), **always load from a `.env` file** in addition to standard environment variables. This is the preferred method because:
- Cursor users cannot `export` env vars that persist across terminal sessions
- `.env` files work consistently across Claude Code, Cursor, and standalone execution
- It avoids the agent ever needing to handle keys directly

## Implementation by Language

**Python** — use `python-dotenv`:
```python
# Add at the top of any script that needs API keys/env vars
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
```

**Node.js / TypeScript** — use `dotenv`:
```javascript
// Add at the top of the entry point
require('dotenv').config();
// or for ESM:
import 'dotenv/config';
```

**Bash** — source `.env` directly:
```bash
# Source .env if it exists (for API keys etc.)
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi
```

**Other languages** — use the language's standard dotenv library (e.g., `godotenv` for Go, `dotenvy` for Rust).

## When to Set Up `.env` Loading

- **Automatically**: When generating evaluation scripts or any code that calls external APIs, include `.env` loading by default. Do not ask the user — just add it.
- **`.env` file creation**: If the script needs keys and no `.env` file exists, ask the user to create one and tell you when it's ready:

> "This script needs an API key to run. Please create a `.env` file in your project root with the key for your chosen provider:
>
> ```
> # For Anthropic (default)
> ANTHROPIC_API_KEY=your-key-here
>
> # For OpenAI
> OPENAI_API_KEY=your-key-here
> ```
>
> Let me know when it's set up and I'll continue."

## Safety Rules

- **Never read `.env` contents** — the agent must never `cat .env`, `grep .env`, or inspect the file
- **Never write keys to `.env`** — the user creates and manages this file themselves
- **Ensure `.env` is gitignored** — when creating a `.env` loading pattern, check that `.env` is in `.gitignore`. If not, add it automatically:

```bash
# Add .env to .gitignore if not already present
grep -qxF '.env' .gitignore 2>/dev/null || echo '.env' >> .gitignore
```

## Cursor Sandbox Restrictions

Cursor runs commands in a sandbox that may block file access — including reading `.env` files. This means `.env` can exist and pass a `test -r` check, but `source .env` or `load_dotenv()` will fail at runtime with a permission error.

**Symptoms:**
- `.env` file exists but evaluation fails with `PermissionError` or similar sandbox denial
- `source .env` silently fails or is blocked
- `python-dotenv` raises an error reading `.env`

**Fix:** The user must configure Cursor to allow file access for evaluation scripts. In the Cursor task or agent configuration, set:

```
required_permissions: ['all']
```

Or configure the specific file access permissions needed.

**During pre-flight**, if you detect a sandbox permission error on `.env` access, tell the user immediately:

> "Cursor's sandbox is blocking `.env` file access. Your evaluation scripts need to read `.env` for API keys.
>
> Please update your Cursor configuration to allow file access:
>
> ```
> required_permissions: ['all']
> ```
>
> Then re-run the evaluation. Let me know when it's updated."

Do not retry or debug further until the user confirms the sandbox is configured. Each failed attempt wastes an evaluation run.
