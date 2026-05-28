from my_claude_code.config import bcolors
from my_claude_code.runtime import create_runtime

def main() -> None:
    runtime = create_runtime()
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
        runtime.agent_loop(history)
        print(bcolors.HEADER + "Agent Response:" + bcolors.ENDC)
        runtime.print_last_response(history)