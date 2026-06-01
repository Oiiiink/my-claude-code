# My Agent System

My version of [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code.git), you can refer to this url for what it's about but don't care much about the details.

- bugs/ contains my big mistakes whening building this project. You can also edit it, but inform the user before doing.
- report/ contains some reports on the prerequisites of this projects that the user is not familiar with, mostly by agents
- tmp/ contains temporary files.
- ../learn-claude-code contains the lcc repo. Read-Only for you.

use pi [agent](https://github.com/earendil-works/pi) as golden standard.

## Answering Style

- use elegant, minimal implementations.
- help me understand, rather than code.
- this is my first project compared to students' toy codes. So you should help me organise my projects. My project manager is `uv`.
- ask me questions to develop a deeper understanding.

## Project Plan

Start with a minimal runnable prototype. Then iterate on it by improving the core agent workflow, making the system more complete, and adding memory modules.

This is my main project for pursuing AI Agent internships, so development should prioritize practical, demonstrable agent capabilities over unnecessary architectural complexity.

More details in `internship-alignment-plan.md`

## Wiki Protocol

This repo has a repo-scoped LLM-maintained wiki at `.agents/llm_wiki/`.

- Read `.agents/llm_wiki/index.md` before non-trivial architecture, refactor, debugging, roadmap, memory, multi-agent, or evaluation work.
- Update `.agents/llm_wiki/` when a stable project fact, design decision, bug lesson, roadmap state, or evaluation conclusion changes.
- Append one entry to `.agents/llm_wiki/log.md` for every wiki update.
- If a relevant task does not need a wiki update, say `wiki unchanged: <reason>` in the final response.
- Keep `tmp/` for temporary run artifacts. Promote only stable conclusions into the wiki.
