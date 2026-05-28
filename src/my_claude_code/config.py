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

# Runtime
WORKDIR = Path.cwd().resolve()
SKILL_DIR = WORKDIR / ".skills"
TRANSCRIPT_DIR = WORKDIR / ".transcripts"
TASK_DIR = WORKDIR / ".tasks"
TEAM_DIR = WORKDIR / ".team"
INBOX_DIR = TEAM_DIR / "inbox"

DEFAULT_MAX_TOKEN = 8000
DEFAULT_CTX_THRESHOLD = 200000