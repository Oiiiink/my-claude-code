from dataclasses import dataclass
from anthropic import Anthropic

from pathlib import Path

from my_claude_code.config import (
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
from my_claude_code.managers.todo import TodoManager
from my_claude_code.managers.skills import SkillLoader
from my_claude_code.managers.tasks import TaskManager
from my_claude_code.managers.background import BackgroundManager
from my_claude_code.managers.team import TeamManager
from my_claude_code.managers.message_bus import MessageBus

@dataclass
class Runtime:
    model_id: str
    workdir: Path
    todo: TodoManager
    skills: SkillLoader
    tasks: TaskManager
    background: BackgroundManager
    team: TeamManager
    bus: MessageBus
    max_tokens: int = DEFAULT_MAX_TOKEN
    _client: Anthropic| None=None

    def agent_loop(self, messages: list) -> None:
        # Placeholder for agent loop logic
        turns_since_todo = 0
        while True:
            micro_compact(messages)
            if estimate_tokens(messages) >= DEFAULT_CTX_THRESHOLD:
                print(bcolors.OKBLUE + "[auto compact triggers]" + bcolors.ENDC)
                messages[:] = auto_compact(messages)
            notifs = BG.draw_notification()
            if notifs:
                notif_text = "\n".join(
                    f"[bg:{n['task_id']}] {n['status']}: {n['result']}" for n in notifs
                )
                messages.append({"role": "user", "content": f"<background-results>\n{notif_text}\n</background-results>"})
            response = self._client.messages.create(
                model=self.model_id,
                max_tokens=self.max_tokens,
                system=self.system_prompt(),
                tools=TOOLS,
                messages=messages
            )
            messages.append({'role':'assistant', 'content':response.content})

            tool_uses = [block for block in response.content if block.type == 'tool_use']
            if not tool_uses:
                break
            
            results = []
            manual_compact = False
            for block in tool_uses:
                print(bcolors.OKBLUE + block.name + bcolors.ENDC)
                handler = TOOL_HANDLERS.get(block.name)
                try:
                    print(block.input)
                    output = handler(**block.input) if handler else f"Unknown Tools, {block.name}"
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
                messages[:] = auto_compact(messages, compact_focus)

    def system_prompt(self):
        return f"""
            You are a coding agent at {self.workdir}.
            Use load_skill to access specialized knowledge before tackling unfamiliar topics.

            Skills available:
            {self.skills.get_descriptions()}
            """

    def print_last_response(self, history: list) -> None:
        response = history[-1]['content']
        if isinstance(response, list):
            for block in response:
                if hasattr(block, 'text'):
                    print(block.text)


    