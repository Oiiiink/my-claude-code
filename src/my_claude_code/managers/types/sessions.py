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
    content: dict[str, Any]
    
@dataclass(frozen=True, kw_only=True)
class AssistantMessage(AgentMessage):
    model: str
    input_tokens: int
    output_tokens: int
    role: str="assistant"
    
@dataclass(frozen=True, kw_only=True)
class UserMessage(AgentMessage):
    role: str="user"

@dataclass(frozen=True, kw_only=True)
class ToolResultMessage(AgentMessage):
    tool_name: str
    tool_call_id: str
    success: bool
    role: str="tool_result"

# Entry
@dataclass(frozen=True, kw_only=True)
class Entry:
    id: str = uuid.uuid4()
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
