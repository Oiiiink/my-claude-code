# CLAUDE.md

@AGENTS.md

## Quick Orientation

Live code is the `src/my_claude_code/` package. The `main.py` and `s_full.py`
at repo root are pre-refactor monolith snapshots — read them only as history,
not as current behavior.

### Package layout

- `__main__.py` / `cli.py` — REPL entry; builds a lead `Runtime` and loops on
  user input.
- `runtime.py` — `Runtime` dataclass and `agent_loop`. Owns the Anthropic
  client, message history, managers, and triggers compaction.
- `config.py` — env vars, `WORKDIR`, and state-dir paths.
- `managers/` — mutable state objects: `TodoManager`, `SkillLoader`,
  `TaskManager`, `BackgroundManager`, `TeamManager`, `MessageBus`.
  `managers/registry.py` chooses which managers to instantiate per role.
- `tools/` — tool handlers grouped by domain (`filesystem`, `shell`, `todo`,
  `skills`, `task_board`, `multi_agents`, `compaction`).
  `tools/registry.py` builds Anthropic tool schemas and dispatches by role.
- `compaction/` — `estimate_tokens`, `micro_compact`, `auto_compact`.

### Roles

`Role = "lead" | "subagent" | "teammate"`. Tools and managers are gated by
role in the two registry modules — when adding capabilities, update both the
tool registry and the role's tool-name list.

### Run

```
uv run python -m my_claude_code
```

Needs `.env` with `MODEL`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_API_KEY` (see
`.env.example`; default points at DeepSeek's Anthropic-compatible endpoint).
`uv` is the project manager — prefer `uv add`, `uv run`, `uv sync` over raw
`pip`/`python`. Python `>=3.12`.

### Runtime state on disk

Created lazily under the working directory and safe to delete to reset:
`.skills/`, `.tasks/`, `.team/inbox/`, `.transcripts/`.

## Wiki caveat

`.agents/llm_wiki/` still describes the project as a single `main.py`. The
package refactor is newer. When wiki and source disagree, trust source and
update the wiki per the protocol in AGENTS.md.
