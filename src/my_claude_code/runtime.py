from dataclasses import dataclass
import os
from anthropic import Anthropic

from pathlib import Path

from dotenv import load_dotenv

from my_claude_code.config import (
    MAIN_NAME,
    MODEL_ID,
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
from my_claude_code.tools import *
from my_claude_code.compaction import *

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

            tool_uses = [block for block in response.content if block.type == 'tool_use']
            if not tool_uses:
                break
            
            results = []
            manual_compact = False
            tool_ctx = ToolContext(actor=self.name, role=self.role, runtime=self, workdir=self.workdir)
            for block in tool_uses:
                print(bcolors.OKBLUE + block.name + bcolors.ENDC)
                try:
                    print(block.input)
                    output = execute_tool(tool_ctx, block.name, **block.input)
                except Exception as e:
                    output = f"<ERROR>Error executing tool {block.name}: {e}</ERROR>"
                print(output[:200])
                results.append({"type" : "tool_result", "tool_use_id" : block.id, 
                            "content" : output})
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
        self.history[:] = auto_compact(self.history, self._client, self.model_id, self.max_tokens // 4, focus)
        
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
        if self.bus is None:
            return
        
        inbox = self.bus.read_inbox(self.name)
        if inbox:
            inbox_text = "\n".join(inbox)
            self.history.append({"role": "user", "content": f"<inbox>\n{inbox_text}\n</inbox>"})

    def print_last_response(self, history: list) -> None:
        response = history[-1]['content']
        if isinstance(response, list):
            for block in response:
                if hasattr(block, 'text'):
                    print(block.text)

def create_runtime(
    name: str=MAIN_NAME,
    role: str="lead",
    model_id: str=MODEL_ID,
    workdir: Path=WORKDIR,
    managers: list[str]=[],
    max_tokens: int=DEFAULT_MAX_TOKEN,
    max_turn: int=None,
    )-> Runtime:
    all = managers == []
    todo = TodoManager() if all or "todo" in managers else None
    skills = SkillLoader(SKILL_DIR) if all or "skills" in managers else None
    tasks = TaskManager(TASK_DIR) if all or "tasks" in managers else None
    background = BackgroundManager() if all or "background" in managers else None
    team = TeamManager(TEAM_DIR) if all or "team" in managers else None
    bus = MessageBus(INBOX_DIR) if all or "team" in managers else None
    load_dotenv(override=True)
    if os.getenv("ANTHROPIC_BASE_URL"):
        os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
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
        _client=client
    )