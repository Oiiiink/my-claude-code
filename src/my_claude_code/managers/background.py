import threading
import subprocess
import uuid

class BackgroundManager:
    def __init__(self):
        self.tasks = {}
        self._notification_queue = []
        self._lock = threading.Lock()

    def run(self, command: str) -> str:
        task_id = str(uuid.uuid4())[:8]
        with self._lock:
            self.tasks[task_id] = {
                "status": "running", "result": None, "command": command
            }
        thread = threading.Thread(target=self._execute, args=(task_id, command), daemon=True)
        thread.start()

        return f"Background task {task_id} started: {command[:80]}"
    
    def _execute(self, task_id: str, command: str):
        try:
            r = subprocess.run(
                command, shell=True, cwd=WORKDIR,
                capture_output=True, text=True, timeout=300
            )
            output = (r.stdout + r.stderr).strip()[:50000]
            status = "completed"
        except subprocess.TimeoutExpired:
            output = "<ERROR>Error: Timeout(300)</ERROR>"
            status = "timeout"
        except Exception as e:
            output = f"<ERROR>Error: {e}</ERROR>"
            status = "error"

        with self._lock:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["result"] = output
            self._notification_queue.append({
                "task_id": task_id,
                "status": status,
                "result": output[:500],
                "command": command[:80]
            })

    def check(self, task_id: str= None) -> str:
        if task_id:
            with self._lock:
                t = self.tasks.get(task_id)
            if not t:
                return f"Unknow task {task_id}"
            return f"{t['status']} {t['command']} : {t['result'] or '(running)'}"
        lines = []
        with self._lock:
            for tid, t in self.tasks.items():
                lines.append(f"{tid} : {t['status']} {t['command'][:80]}")
        return '\n'.join(lines) or "(No background task)"
    
    def draw_notification(self) -> list[dict]:
        with self._lock:
            notifs = list(self._notification_queue)
            self._notification_queue.clear()
        return notifs
