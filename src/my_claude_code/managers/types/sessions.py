from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
from typing import Any
import uuid

# AgentMessage
@dataclass(frozen=True, kw_only=True)
class AgentMessage:
    role: str
    
@dataclass(frozen=True, kw_only=True)
class AssistantMessage(AgentMessage):
    role: str="assistant"
    model: str
    input_tokens: int
    output_tokens: int
    content: dict[str, Any] | list[dict[str, Any]]
    
@dataclass(frozen=True, kw_only=True)
class UserMessage(AgentMessage):
    role: str="user"
    content: dict[str, Any]

@dataclass(frozen=True, kw_only=True)
class ToolResultMessage(AgentMessage):
    role: str="tool_result"
    tool_name: str
    tool_call_id: str
    success: bool
    truncated: bool
    nbytes: int
    content: dict[str, Any]

# Entry
@dataclass(frozen=True, kw_only=True)
class Entry:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone(timedelta(hours=8))).isoformat())
    type: str="entry"
    
@dataclass(frozen=True, kw_only=True)
class SessionEntry(Entry):
    cwd: Path
    type: str="session"
    
@dataclass(frozen=True, kw_only=True)
class MessageEntry(Entry):
    message: AgentMessage
    type: str="message"
    
@dataclass(frozen=True, kw_only=True)
class CompactEntry(Entry):
    focus: str
    before: dict[str, Any]
    after: dict[str, Any]
    type: str="compact"
