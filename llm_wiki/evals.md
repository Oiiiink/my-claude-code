# Evaluations

No durable coding-agent eval layer is present in the current source tree.
Ignore stale legacy eval claims until new artifacts land.

## Current Evidence

- `test/test_sessions.py` exists, but it is a session-log regression test, not an eval harness.
- A local verification run on 2026-06-05 used `.venv/bin/python`, disabled bytecode/cache writes, set `MODEL=dummy`, and ran `test/test_sessions.py`.
- Result: one test passed and one failed. Failure cause: `SessionsManager` emits `nbytes`, while the test expects `output_bytes`.

## Current Logging Seed

`SessionsManager` writes `.sessions/session_<id>.jsonl` with session/message/tool
result/compact entries. This is useful as the capture seed for future eval and
trajectory projection, but it is not yet enough for Stage 2 or Stage 3.

## Target Eval Direction

Next eval work should build:

- structured `run_tests` tool;
- mini task-spec schema for local coding tasks;
- isolated task fixtures;
- bounded edit/test/retry loop;
- score report with pass rate, iterations, tool calls, wall time, and failure states;
- trajectory projection from captured session/tool events.
