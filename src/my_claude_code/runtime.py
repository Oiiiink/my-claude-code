from dataclasses import dataclass
import json
import os
from anthropic import Anthropic

from pathlib import Path

from dotenv import load_dotenv

from my_claude_code.config import (
    MAIN_NAME,
    MODEL_ID,
    SESSIONS_DIR,
    WORKDIR,
    SKILL_DIR,
    TRANSCRIPT_DIR,
    TASK_DIR,
    TEAM_DIR,
    INBOX_DIR,
    DEFAULT_MAX_TOKEN,
    DEFAULT_CTX_THRESHOLD,
    bcolors,
)
from my_claude_code.managers import *
from my_claude_code.managers.sessions import SessionsManager
from my_claude_code.managers.types.sessions import AgentMessage, AssistantMessage, MessageEntry
from my_claude_code.tools import *
from my_claude_code.compaction import *
from my_claude_code.tools.registry import run_tool_call, ToolCall

@dataclass
class Runtime:
    model_id: str
    name: str
    role: str
    workdir: Path
    todo: TodoManager
    skills: SkillLoader
    tasks: TaskManager
    background: BackgroundManager
    sessions: SessionsManager
    team: TeamManager
    bus: MessageBus
    max_tokens: int
    max_turn: int
    history: list[dict]
    _client: Anthropic| None=None

    def agent_loop(self) -> None:
        # Placeholder for agent loop logic
        turns_since_todo = 0
        turns = 0
        messages = self.history
        
        while self.max_turn is None or turns < self.max_turn:
            turns += 1
            self._micro_compact()
            if estimate_tokens(messages) >= DEFAULT_CTX_THRESHOLD:
                print(bcolors.OKBLUE + "[auto compact triggers]" + bcolors.ENDC)
                self._auto_compact()
            self._bg_notification()
            self._inbox_notification()
            response = self._client.messages.create(
                model=self.model_id,
                max_tokens=self.max_tokens,
                system=self.system_prompt(),
                tools=build_tools(self.role),
                messages=messages
            )
            messages.append({'role':'assistant', 'content':response.content})
            self.sessions.append_assistant_message(response)

            tool_calls = [block for block in response.content if block.type == 'tool_use']
            if not tool_calls:
                break
            
            results = []
            manual_compact = False
            tool_ctx = ToolContext(actor=self.name, role=self.role, runtime=self, workdir=self.workdir)
            for block in tool_calls:
                print(bcolors.OKBLUE + block.name + bcolors.ENDC)
                tool_call = ToolCall(name=block.name, input=block.input, id=block.id)
                tool_result = run_tool_call(tool_ctx, tool_call)
                results.append(tool_result.to_anthropic_tool_result())
                self.sessions.append_tool_result(tool_result)
                if block.name == "todo":
                    turns_since_todo = -1
                elif block.name == "compact":
                    manual_compact = True
                    compact_focus = block.input.get("focus")
            turns_since_todo += 1
            if turns_since_todo > 5:
                results.append({"type": "text", "text": "<reminder>Remember to use the todo tool to manage your tasks!</reminder>"})
            messages.append({"role" : "user", "content" : results})

            if manual_compact:
                print(bcolors.OKBLUE + "[manual compact]" + bcolors.ENDC)
                self._auto_compact(compact_focus)

    def system_prompt(self):
        return f"""
            You are a coding agent at {self.workdir}. Your name is {self.name}. 
            You can work for at most {'infinite' if self.max_turn is None else self.max_turn} turns. 
            Use load_skill to access specialized knowledge before tackling unfamiliar topics.

            Skills available:
            {self.skills.get_descriptions()}
            """

    def _auto_compact(self, focus: str| None=None):
        before = estimate_tokens(self.history)
        self.history[:], transcript_path = compact(self.history, self._client, self.model_id, self.max_tokens // 4, focus)
        after = estimate_tokens(self.history)
        self.sessions.append_compact_entry(focus=focus or "no focus", before=before, after=after, transcript_path=transcript_path)
        
    def _micro_compact(self):
        micro_compact(self.history)

    def _bg_notification(self):
        if self.background is None:
            return
        
        notifs = self.background.draw_notification()
        if notifs:
            notif_text = "\n".join(
                f"[bg:{n['task_id']}] {n['status']}: {n['result']}" for n in notifs
            )
            self.history.append({"role": "user", "content": f"<background-results>\n{notif_text}\n</background-results>"})

    def _inbox_notification(self):
        if self.bus is None or self.role == "lead":
            return
        
        inbox = self.bus.read_inbox(self.name)
        if inbox:
            inbox_text = "\n".join(json.dumps(m, ensure_ascii=False) for m in inbox)
            self.history.append({"role": "user", "content": f"<inbox>\n{inbox_text}\n</inbox>"})

    def print_last_response(self) -> None:
        response = self.history[-1]['content']
        if isinstance(response, list):
            for block in response:
                if hasattr(block, 'text'):
                    print(block.text)

def create_runtime(
    name: str=MAIN_NAME,
    role: str="lead",
    model_id: str=MODEL_ID,
    workdir: Path=WORKDIR,
    managers: list[str]=get_managers("lead"),
    max_tokens: int=DEFAULT_MAX_TOKEN,
    max_turn: int=None,
    sessions_dir: Path=SESSIONS_DIR
    )-> Runtime:
    all = managers == []
    todo = TodoManager() if all or "todo" in managers else None
    skills = SkillLoader(SKILL_DIR) if all or "skills" in managers else None
    tasks = TaskManager(TASK_DIR) if all or "tasks" in managers else None
    background = BackgroundManager() if all or "background" in managers else None
    team = TeamManager(TEAM_DIR) if all or "team" in managers else None
    bus = MessageBus(INBOX_DIR) if all or "team" in managers else None
    sessions = SessionsManager(sessions_dir=sessions_dir, cwd=workdir) if all or "sessions" in managers else None
    client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
    return Runtime(
        model_id=model_id,
        name=name,
        role=role,
        workdir=workdir,
        todo=todo,
        skills=skills,
        tasks=tasks,
        background=background,
        team=team,
        bus=bus,
        max_tokens=max_tokens,
        max_turn=max_turn,
        history=[],
        _client=client,
        sessions=sessions,
    )