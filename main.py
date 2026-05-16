import os
import subprocess
import re
import yaml
import time
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from pathlib import Path

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TodoManager:
    def __init__(self):
        self.items = []
        self.MAX_STEPS = 10

    def update(self, items):
        if len(items) > self.MAX_STEPS:
            return f"<ERROR>Too many todo items, max is {self.MAX_STEPS}</ERROR>"
        validated = []
        in_progress_count = 0
        for item in items:
            if not item.get("id"):
                return "<ERROR>Todo item must have an id</ERROR>"
            if not item.get("content"):
                return "<ERROR>Todo item must have content</ERROR>"
            if item.get("status") not in ["pending", "in_progress", "done"]:
                return "<ERROR>Todo item status must be pending, in_progress, or done</ERROR>"
            validated.append(item)
            if item["status"] == "in_progress":
                in_progress_count += 1
            if in_progress_count > 1:
                return "<ERROR>Only one todo item can be in_progress at a time</ERROR>"
        self.items = validated

        return self.render()

    def render(self):
        if not self.items:
            return "Todo list is empty."
        lines = ["Todo List:"]
        for item in self.items:
            status_icon = {"pending": "⏳", "in_progress": "🚀", "done": "✅"}.get(item["status"], "")
            lines.append(f"{status_icon} [{item['id']}] {item['content']}")
        return "\n".join(lines)

class SkillLoader:
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.skills = {}
        self._load_all()

    def _load_all(self):
        if not self.skills_dir.exists():
            return
        
        for f in sorted(self.skills_dir.rglob("SKILL.md")):
            text = f.read_text()
            meta, body = self._parse_frontmatter(text)
            name = meta.get("name", f.parent.name)
            self.skills[name] = {"meta": meta, "body": body, "path": str(f)}

    def _parse_frontmatter(self, text:str):
        """Parse YAML frontmatter between --- delimiters."""
        match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
        if not match:
            return {}, text
        try:
            meta = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            meta = {}
        return meta, match.group(2).strip()

    def get_descriptions(self):
        """Layer 1: get short descriptions of all skills for the system prompts"""
        if not self.skills:
            return f"(no skills available)"
        
        lines = []
        for name, skill in self.skills.items():
            desc = skill["meta"].get("descriptipn", "No description")
            tags = skill["meta"].get("tags", "")
            line = f"  - {name}: {desc}"
            if tags:
                line += f" [{tags}]"
            lines.append(line)
        return '\n'.join(lines)

    def get_content(self, name:str):
        """Layer 2 : get full skill body if the modle use load_skill"""
        skill = self.skills.get(name)
        if not skill:
            return f"ERROR: Unknown skill {name}. Available: {',.'.join(self.skills.keys())}"
        return f"<skill name=\"{name}\">\n{skill['body']}\n</skill>"

# Config
WORKDIR = Path.cwd().resolve()
SKILL_DIR = WORKDIR / ".skills"
TRANSCRIPT_DIR = WORKDIR / ".transcripts"
TODO = TodoManager()
SKILL_LOADER = SkillLoader(SKILL_DIR)
load_dotenv(override=True)
if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL_ID = os.environ["MODEL"]
MAX_TOKENS = 8000
SYSTEM = f"""
You are a coding agent at {os.getcwd()}.
Use load_skill to access specialized knowledge before tackling unfamiliar topics.

Skills available:
{SKILL_LOADER.get_descriptions()}
"""
SUBAGENT_SYSTEM = f"""
You are a coding subagent at {WORKDIR}. Complete the given task, then summarize your findings.
Use load_skill to access specialized knowledge before tackling unfamiliar topics.

Skills available:
{SKILL_LOADER.get_descriptions()}
"""

THRESHOLD = 200000
KEEP_RECENT = 3
PRESERVE_RESULT_TOOLS = {"read_file"}

CHILD_TOOLS = [
    {
        "name" : "bash",
        "description" : "Run a shell command.", 
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string", "description": "a bash command that is runnable directly."}},
            "required": ["command"],
            "additionalProperties": False
        }
    },
    {
        "name" : "read_file",
        "description" : "Read a file",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "limit": {"type": "integer", "description": "max lines to read"}},
            "required": ["path", "limit"],
            "additionalProperties": False
        }
    },
    {
        "name": "write_file",
        "description": "write something into a file",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
            "additionalProperties": False
        }
    },
    {
        "name": "edit_file",
        "description": "edit part of a file",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}},
            "required": ["path", "old_text", "new_text"],
            "additionalProperties": False
        }
    },
    {
        "name": "todo",
        "description": "manage your todo list for complex task to get better results.",
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "content": {"type": "string"},
                            "status": {"type": "string", "enum": ["pending", "in_progress", "done"]}
                        },
                        "required": ["id", "content", "status"],
                        "additionalProperties": False       
                    }
                }
            },
            "required": ["items"],
            "additionalProperties": False
        }
    },
    {
        "name": "load_skill",
        "description": "Load specialized knowledge by name",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
            "additionalProperties": False
        }
    },
]

TOOLS = CHILD_TOOLS + [
    {
        "name" : "task",
        "description" : "Spawn a subagent with fresh context to reduce context rot. It shares filesystems but not conversation history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The task prompt for the subagent."
                }
            },
            "required": ["prompt"],
            "additionalProperties": False
        }
    },
        {
        "name": "compact",
        "description": "Trigger manual conversation compression to reduce context window usage.",
        "input_schema": {
            "type": "object",
            "properties": {"focus": {"type": "string", "description": "what to preserve in the summary."}},
            "required": [],
            "additionalProperties": False
        }
    },
]

TOOL_HANDLERS = {
    "bash" :        lambda **kwargs : run_bash(kwargs["command"]),
    "read_file" :   lambda **kwargs : run_read(kwargs["path"], kwargs["limit"]),
    "write_file":   lambda **kwargs : run_write(kwargs["path"], kwargs["content"]),
    "edit_file" :   lambda **kwargs : run_edit(kwargs["path"], kwargs["old_text"], kwargs["new_text"]),
    "todo" :        lambda **kwargs : TODO.update(kwargs["items"]),
    "load_skill" :  lambda **kwargs : SKILL_LOADER.get_content(kwargs["name"]),
    "task" :        lambda **kwargs : run_subagent(kwargs["prompt"]),
    "compact":      lambda **kwargs : "Manual compression requested.",
}

# Tools
def safe_path(path: str) -> Path:
    fp = (WORKDIR / path).resolve()
    if not fp.is_relative_to(WORKDIR):
        raise ValueError(f"Path escape working directory: {fp}")
    return fp

def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"] # Too broad
    if any(d in command for d in dangerous):
        return f"Error: Dangerous command blocked"
    try:
        r = subprocess.run(command, shell=True, cwd=os.getcwd(),
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"

def run_read(path: str, limit: int = None) -> str:
    try:
        text = safe_path(path).read_text(encoding="utf-8")
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"

def run_write(path: str, content: str) -> str:
    try:
        fp = safe_path(path)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"

def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        fp = safe_path(path)
        content = fp.read_text(encoding="utf-8")
        if old_text not in content:
            return f"Error: Text not found in {path}"
        fp.write_text(content.replace(old_text, new_text, 1))
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"

def run_subagent(prompt: str) -> str:
    sub_history = [{"role": "user", "content": prompt}]

    turns_since_todo = 0
    for _ in range(30):
        response = client.messages.create(
            model=MODEL_ID, max_tokens=MAX_TOKENS, system=SUBAGENT_SYSTEM,
            tools=CHILD_TOOLS, messages=sub_history
        )

        sub_history.append({"role": "assistant", "content": response.content})
        tool_uses = [b for b in response.content if b.type == "tool_use"]

        if not tool_uses:
            break

        results = []
        for block in tool_uses:
            handler = TOOL_HANDLERS.get(block.name)
            try:
                output = handler(**block.input) if handler else f"Unknown Tools, {block.name}"
            except Exception as e:
                output = f"Error executing tool {block.name}: {e}"
            print(output[:200])
            results.append({"type" : "tool_result", "tool_use_id" : block.id, 
                        "content" : output})
            if block.name == "todo":
                turns_since_todo = -1
        turns_since_todo += 1
        if turns_since_todo > 5:
            results.append({"type": "text", "text": "<reminder>Remember to use the todo tool to manage your tasks!</reminder>"})
        sub_history.append({"role" : "user", "content" : results})
    
    return "".join(b.text for b in response.content if hasattr(b, "text")) or "(no summary)"

def estimate_tokens(messages: list) -> int:
    return len(str(messages)) // 4

def micro_compact(messages: list):
    tool_name_map = {}
    tool_results = []

    for msg in messages:
        if msg["role"] == "assistant" and isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if getattr(block, "type", None) == "tool_use":
                    tool_name_map[block.id] = block.name

        if msg["role"] == "user" and isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    tool_results.append(block)

    for result in tool_results[:-KEEP_RECENT]:
        content = result.get("content", "")
        tool_name = tool_name_map.get(result.get("tool_use_id"), "")

        if (
            tool_name
            and isinstance(content, str)
            and len(content) > 100
            and tool_name not in PRESERVE_RESULT_TOOLS
        ):
            result["content"] = f"[Previous: used {tool_name}]"

def auto_compact(messages: list, focus: str|None=None) -> list:
    focus = "no focus" if not focus else focus
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(json.dumps(msg, default=str) for msg in messages))

    print(bcolors.OKBLUE + f"transcript saved in {transcript_path}" + bcolors.ENDC)

    conversation_text = json.dumps(messages, default=str)[-80000:]
    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=MAX_TOKENS//4,
        messages=[{"role":"user", "content":
                    "Summarize this conversation for continuity. Include: "
                    "1) What was accomplished, 2) Current state, 3) Key decisions made. 4) What to do next"
                    f"Focus: {focus}. Be concise but preserve critical details.\n\n" + conversation_text}]
    )

    summary = next((block.text for block in response.content if hasattr(block, "text")), "")
    if not summary:
        summary = "(no summary)"
    return [{"role": "user", "content": f"[Conversation compressed] transcript path:{transcript_path}\n\n{summary}"}]

# Core loop
def agent_loop(messages : list):
    turns_since_todo = 0
    while True:
        micro_compact(messages)
        if estimate_tokens(messages) >= THRESHOLD:
            print(bcolors.OKBLUE + "[auto compact triggers]" + bcolors.ENDC)
            messages[:] = auto_compact(messages)
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=MAX_TOKENS,
            system=SYSTEM,
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
                output = f"Error executing tool {block.name}: {e}"
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
    

if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input(bcolors.HEADER + 'Start your request: ' + bcolors.ENDC)
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ['q', 'quit', '']:
            print(bcolors.HEADER + 'agent ended' + bcolors.ENDC)
            break
        history.append({'role':'user', 'content':query})
        agent_loop(history)
        response = history[-1]['content']
        print(bcolors.OKGREEN + "Agent Response:" + bcolors.ENDC)
        if isinstance(response, list):
            for block in response:
                if hasattr(block, 'text'):
                    print(block.text)
        print()
