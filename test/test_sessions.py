import json
from my_claude_code.managers.sessions import SessionsManager
from my_claude_code.tools.contracts import ToolResult

def _read(p): return [json.loads(l) for l in p.read_text().splitlines()]

def test_entry_ids_unique(tmp_path):                 # P0 guard
    s = SessionsManager(sessions_dir=tmp_path, cwd=tmp_path)
    s.append_user_message("hi")
    s.append_tool_result(ToolResult("bash", "t1", "ok", True))
    ids = [e["id"] for e in _read(s.sessions_file)]
    assert len(ids) == len(set(ids)), ids

def test_tool_output_truncated(tmp_path):            # drives Fix 2
    s = SessionsManager(sessions_dir=tmp_path, cwd=tmp_path)
    s.append_tool_result(ToolResult("read_file", "t2", "x" * 10_000, True))
    m = _read(s.sessions_file)[-1]["message"]
    assert m["truncated"] and m["nbytes"] == 10_000
    assert len(m["content"]["text"]) <= 4000