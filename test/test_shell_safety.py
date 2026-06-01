from my_claude_code.tools import ToolContext
from my_claude_code.tools.shell import bash
from my_claude_code.runtime import create_runtime
from pathlib import Path

def make_test_context():
    tmp = Path.cwd().resolve() / "tmp"
    tmp.mkdir(exist_ok=True)
    runtime = create_runtime(workdir=tmp)
    return ToolContext(actor=runtime.name, role=runtime.role, workdir=tmp, runtime=runtime)

def return_error(output: str) -> bool:
    return output.startswith("<ERROR>") and output.endswith("</ERROR>")

def test_bash_safe_command(cmd: str):
    ctx = make_test_context()
    output = bash(ctx, cmd)
    assert not return_error(output), f"Safe command '{cmd}' should not return an error
    
def test_bash_dangerous_command(cmd: str):
    ctx = make_test_context()
    output = bash(ctx, cmd)
    assert return_error(output), f"Dangerous command '{cmd}' should return an error
    
SAFE_COMMANDS = [
    
]    

if __name__ == "__main__":