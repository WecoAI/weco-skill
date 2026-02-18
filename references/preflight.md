# Environment Pre-flight

**Run this checklist before any evaluation (baseline or optimization).**

Environment issues — missing package managers, broken virtual environments, inaccessible `.env` files, missing dependencies — cause evaluation failures that look like optimization failures. Catching them upfront in a single pass prevents cascading debug cycles.

## Pre-flight Checklist

### 1. Detect Language and Package Manager

Identify what's available in the project environment:

| Language | Check for (in order) | Dependency Files |
|----------|----------------------|-----------------|
| Python | `uv`, `pip`, `poetry`, `conda` | `requirements.txt`, `pyproject.toml`, `setup.py` |
| Node.js | `npm`, `yarn`, `pnpm`, `bun` | `package.json` |
| Rust | `cargo` | `Cargo.toml` |
| Go | `go` | `go.mod` |
| Ruby | `bundle` | `Gemfile` |

```bash
# Example: detect Python package manager
which uv 2>/dev/null && echo "uv" || \
which pip 2>/dev/null && echo "pip" || \
which poetry 2>/dev/null && echo "poetry" || \
which conda 2>/dev/null && echo "conda" || \
echo "NONE"
```

**If no package manager is found**, tell the user what's needed and wait:

> "I need a Python package manager to install evaluation dependencies. Please install one:
>
> - `uv` (recommended):
>   - **macOS**: `brew install uv`
>   - **Linux/macOS**: `pip install uv`
>   - **From source** (download first, then run):
>     ```
>     curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh
>     sh /tmp/uv-install.sh
>     ```
> - `pip`: Usually included with Python (`python -m ensurepip`)
>
> Let me know when it's ready."

**Record which package manager is available** — you'll need it for dependency installation and for fixing missing packages during optimization.

### 2. Create Isolated Environment (if applicable)

Some languages need virtual environments to avoid polluting the user's system. Create one inside the task directory:

**Python with uv:**
```bash
cd .weco/<task>
uv venv .venv
source .venv/bin/activate
```

**Python with pip/venv:**
```bash
cd .weco/<task>
python -m venv .venv
source .venv/bin/activate
```

**Python with conda:**
```bash
conda create -p .weco/<task>/.venv python=3.11 -y
conda activate .weco/<task>/.venv
```

**Node.js, Rust, Go, Ruby:** These use project-local dependency management by default (`node_modules/`, `target/`, `vendor/`). No virtual environment needed — skip this step.

**Important:** Always create the environment inside the task directory (`.weco/<task>/.venv`) so it doesn't interfere with the user's project environment.

### 3. Install Dependencies

Install all packages required by the evaluation script **before** the first run:

**Python:**
```bash
# Install evaluation dependencies
pip install anthropic python-dotenv  # or uv pip install ...

# If the project has a requirements file, install those too
pip install -r requirements.txt 2>/dev/null || true
```

**Node.js:**
```bash
npm install  # or yarn install, pnpm install
```

**Other languages:** Use the standard dependency installation command for the language's package manager.

**Key point:** Install now, not later. Discovering missing packages during optimization step 3 of 10 wastes time and Weco credits.

### 4. Verify .env Accessibility

Check that `.env` exists and is readable **without reading its contents**:

```bash
# Check .env exists and is readable (NOT its contents)
test -r .env && echo ".env: OK" || \
test -r ../../.env && echo "Project root .env: OK" || \
echo ".env: NOT FOUND"
```

If the evaluation needs API keys and no `.env` is found, prompt the user:

> "The evaluation script needs `ANTHROPIC_API_KEY`. Please create a `.env` file in your project root:
>
> ```
> ANTHROPIC_API_KEY=your-key-here
> ```
>
> Let me know when it's set up."

Do not proceed until `.env` is confirmed accessible.

**Also verify `.env` is gitignored.** Check whether `.env` is listed in `.gitignore`. If not, ask the user before adding it:

> "I notice `.env` isn't in your `.gitignore`. Can I add it to prevent accidentally committing secrets?"

If the user confirms:

```bash
echo '.env' >> .gitignore
```

See `references/api-keys.md` for details on `.env` safety rules.

### 5. Dry-Run the Evaluation Script

Run the evaluation script once end-to-end as a smoke test:

```bash
bash .weco/<task>/evaluate.sh
```

**Check the output for:**

| Error Pattern | Fix |
|---------------|-----|
| `ModuleNotFoundError` / `Cannot find module` | Install the missing package |
| `PermissionError` / `Permission denied` | `chmod +x` the script, or check sandbox restrictions (see below) |
| `FileNotFoundError` | Check paths, copy missing data files |
| API authentication errors | Prompt user to check `.env` (without reading it) |
| Model not found / unavailable | Fix model ID (see `references/models.md`) |
| Sandbox denial on `.env` or venv | **Cursor sandbox** — tell user to set `required_permissions: ['all']` (see `references/api-keys.md`) |

**Cursor users:** If the dry-run fails with permission errors on `.env` or virtual environment operations, this is almost certainly a sandbox restriction — not a file permission issue. See "Cursor Sandbox Restrictions" in `references/api-keys.md`. Do not waste attempts debugging file permissions; address the sandbox configuration first.

**If the dry-run succeeds:** The environment is ready. Proceed with baseline measurement.

**If it fails:** Fix the issue, re-run the dry-run, and repeat until it passes. Do not proceed to baseline or optimization until the dry-run completes successfully.

## Pre-flight in evaluate.sh

The `evaluate.sh` wrapper should handle environment activation automatically so each Weco step runs in the correct environment:

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

Adapt the last line for the project's language (e.g., `node evaluate.js`, `cargo run`, etc.).
