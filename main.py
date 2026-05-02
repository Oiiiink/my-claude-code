import os
import subprocess
from anthropic import Anthropic
from dotenv import load_dotenv

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

# Config
load_dotenv(override=True)
if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL_ID = os.environ["MODEL"]
MAX_TOKENS = 8000
SYSTEM = f"""
You are a coding agent at {os.getcwd()}.
"""

TOOLS = [
    {
        "name" : "bash",
        "description" : "Run a shell command", 
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        }
    }
]

# Tools
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

# Core loop
def agent_loop(messages : list):
    while True:
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=MAX_TOKENS,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages
        )
        messages.append({'role':'assistant', 'content':response.content})
        if response.stop_reason != 'tool_use':
            return
        
        results = []
        for block in response.content:
            if block.type == 'tool_use':
                print(bcolors.OKBLUE + block.input["command"] + bcolors.ENDC)
                output = run_bash(block.input["command"])
                print(output[:200])
                results.append({"type" : "tool_result", "tool_use_id" : block.id, 
                            "content" : output})
        messages.append({"role" : "user", "content" : results})
    

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
        if isinstance(response, list):
            for block in response:
                if hasattr(block, 'text'):
                    print(block.text)
        print()
