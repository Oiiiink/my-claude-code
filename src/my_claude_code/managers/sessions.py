from pathlib import Path
from dataclasses import asdict, dataclass
import json
import uuid

from my_claude_code.compaction.compaction import estimate_tokens
from my_claude_code.managers.types.sessions import AssistantMessage, CompactEntry, MessageEntry, SessionEntry, ToolResultMessage, UserMessage
from my_claude_code.tools.contracts import ToolResult


MAX_LOGGED_OUTPUT_CHARS = 4000

def truncate(text: str) -> tuple[str, int, bool]:
    nbytes = len(text.encode("utf-8"))
    if len(text) <= MAX_LOGGED_OUTPUT_CHARS:
        return text, nbytes, False
    return text[:MAX_LOGGED_OUTPUT_CHARS], nbytes, True

class SessionsManager:
    def __init__(self, sessions_dir: Path, cwd: Path):
        self.sessions_dir = sessions_dir.resolve()
        self.session_id = uuid.uuid4().hex
        self.cwd = cwd.resolve()
        self.sessions_file = self.sessions_dir / f"session_{self.session_id}.jsonl"
        self.entries = []
        
        self.sessions_dir.mkdir(exist_ok=True)
        self.append_entry(SessionEntry(id=self.session_id, cwd=self.cwd))
        
    def append_entry(self, entry: SessionEntry | MessageEntry | CompactEntry):
        self.entries.append(entry)
        with open(self.sessions_file, "a") as f:
            json.dump(asdict(entry), fp=f, default=str, ensure_ascii=False)
            f.write("\n")
        
    def append_user_message(self, content: str):
        self.append_entry(MessageEntry(message=UserMessage(role="user", content={"text": content})))
        
    def append_assistant_message(self, response):
        if isinstance(response.content, list):
            content = [block.model_dump() if hasattr(block, 'model_dump') else block.__dict__ for block in response.content]
        self.append_entry(MessageEntry(message=AssistantMessage(
            content=content,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens
        )))
        
    def append_tool_result(self, tool_result: ToolResult):
        raw = tool_result.output if isinstance(tool_result.output, str) else json.dumps(tool_result.output, ensure_ascii=False)
        truncated, nbytes, truncated_flag = truncate(raw)
        self.append_entry(MessageEntry(message=ToolResultMessage(
            tool_name=tool_result.tool_name,
            tool_call_id=tool_result.tool_call_id,
            success=tool_result.success,
            truncated=truncated_flag,
            nbytes=nbytes,
            content={
                "type": "text",
                "text": truncated,
            }
        )))
        
    def append_compact_entry(self, focus:str, before: dict, after: dict):
        before_sta = {"token_counts": estimate_tokens(before), "messages": json.dumps(before, default=str, ensure_ascii=False)}
        after_sta = {"token_counts": estimate_tokens(after), "messages": json.dumps(after, default=str, ensure_ascii=False)}
        self.append_entry(CompactEntry(focus=focus, before=before_sta, after=after_sta))