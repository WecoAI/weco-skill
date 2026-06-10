# Model Reference

Use these model IDs when generating evaluation scripts. **Always use aliases** (not dated snapshot IDs) so scripts stay current.

## Anthropic Models

| Model | API ID | Cost (in/out per MTok) | Use For |
|-------|--------|------------------------|---------|
| Claude Opus 4.6 | `claude-opus-4-6` | $5 / $25 | Best judge model, complex evaluation |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` | $3 / $15 | Default skill/prompt execution, good judge |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1 / $5 | User simulator, input detection, cheap tasks |

**Legacy (still available):**

| Model | API ID | Cost (in/out per MTok) |
|-------|--------|------------------------|
| Claude Sonnet 4 | `claude-sonnet-4-0` | $3 / $15 |
| Claude Haiku 3 | `claude-3-haiku-20240307` | $0.25 / $1.25 |

## OpenAI Models

| Model | API ID | Use For |
|-------|--------|---------|
| GPT-5.2 | `gpt-5.2` | Latest flagship |
| GPT-5 | `gpt-5` | Flagship |
| GPT-5 Mini | `gpt-5-mini` | Cost-effective |
| GPT-5 Nano | `gpt-5-nano` | Cheapest |
| GPT-4.1 | `gpt-4.1` | Reliable, well-tested |
| GPT-4.1 Mini | `gpt-4.1-mini` | Cost-effective |
| GPT-4.1 Nano | `gpt-4.1-nano` | Cheapest |
| GPT-4o | `gpt-4o` | Previous flagship |
| GPT-4o Mini | `gpt-4o-mini` | Previous cost-effective |
| o4 Mini | `o4-mini` | Reasoning |
| o3 | `o3` | Reasoning |

## Default Model Assignments for Evaluation

**Anthropic (default):**

| Role | Default | Why |
|------|---------|-----|
| Skill/prompt execution (agent under test) | `claude-sonnet-4-5` | Good balance of capability and cost |
| User simulator | `claude-haiku-4-5` | Cheap, fast, sufficient for simulation |
| Input detection (`needs_user_input`) | `claude-haiku-4-5` | Binary classification, cheapest model works |
| Transcript/response judge | `claude-sonnet-4-5` | Needs good judgment; upgrade to `claude-opus-4-6` for high-stakes |

**OpenAI alternative:**

| Role | Default | Why |
|------|---------|-----|
| Skill/prompt execution | `gpt-4.1` | Reliable, well-tested |
| User simulator | `gpt-4.1-mini` | Cost-effective |
| Input detection | `gpt-4.1-nano` | Cheapest, sufficient for binary classification |
| Transcript/response judge | `gpt-4.1` | Good judgment; upgrade to `o3` for high-stakes |

Ask the user which provider they prefer. The evaluation templates support both — set `PROVIDER = "anthropic"` or `PROVIDER = "openai"` at the top of the evaluation script.

## Model Validation (Required Before Evaluation)

**Before running any evaluation**, validate that the configured models are available on the user's API key. The evaluation templates include a `validate_models()` function that sends a single-token smoke test to each configured model. If a model fails, tell the user which model is unavailable and suggest alternatives from the table above. Do not proceed with evaluation until all models validate successfully.

## Provider Abstraction

The evaluation templates use a `chat()` helper function that works with both Anthropic and OpenAI. Set `PROVIDER = "anthropic"` or `PROVIDER = "openai"` at the top of the evaluation script:

```python
# =============================================================================
# PROVIDER CONFIGURATION
# =============================================================================

# Set to "anthropic" or "openai"
PROVIDER = "anthropic"


def chat(model, messages, system=None, max_tokens=1024):
    """Send a chat request to the configured provider.

    Works with both Anthropic and OpenAI APIs.
    """
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


def validate_models(*model_ids):
    """Smoke test model availability before running evaluation."""
    all_ok = True
    for model_id in set(model_ids):
        try:
            chat(model_id, [{"role": "user", "content": "hi"}], max_tokens=1)
            print(f"  ok: {model_id}", file=sys.stderr)
        except Exception as e:
            print(f"  FAILED: {model_id} - {e}", file=sys.stderr)
            all_ok = False
    return all_ok
```

All template functions (`run_with_prompt`, `judge_response`, `run_scenario`, etc.) use `chat()` instead of calling the Anthropic or OpenAI client directly.
