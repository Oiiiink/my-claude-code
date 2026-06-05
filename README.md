# README

My version of [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code.git)

## Quickstart

This is a Python 3.12 project managed by `uv`.

```bash
uv sync --dev
cp .env.example .env
```

Edit `.env` with your Anthropic-compatible endpoint, API key, and `MODEL`.
Then start the CLI agent:

```bash
uv run python -m my_claude_code
```

At the prompt, enter a coding task. Use `q`, `quit`, or an empty input to exit.

For local verification, run:

```bash
uv run python -m pytest
```

## Project Direction

This project should grow into a minimal Coding Agent Engineering Harness: a runnable tool-calling agent with safe tools, task execution, events logging, multi-agent coordination, memory, and benchmark-style evaluation.

## What's next

- hooks for safety: OK (add user approval, maybe extended to hooks)
- logging for replay: OK(easy version, will be refined after feedback loop)
- feedback loop:
- evaluation for performance:
- navigation tools:
- multi-agents:
- async and promise:

`Hide multi-agent first `
