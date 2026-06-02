from pathlib import Path
import json

TASK_STATUS = ["pending", "in_progress", "completed"]

class TaskManager:
    def __init__(self, task_dir: Path):
        self.task_dir = task_dir
        self.task_dir.mkdir(exist_ok=True)
        self.next_id = self._max_id() + 1

    def _max_id(self):
        ids = [int(f.stem.split("_")[1]) for f in self.task_dir.glob("task_*.json")]
        return max(ids) if ids else 0

    def _load(self, task_id: int) -> dict:
        task_path = self.task_dir / f"task_{task_id}.json"
        if not task_path.exists():
            return {}
        return json.loads(task_path.read_text(encoding='utf-8'))

    def _save(self, task: dict):
        task_path = self.task_dir / f"task_{task['id']}.json"
        task_path.write_text(json.dumps(task, indent=2, ensure_ascii=False))
    
    def _clear_dependency(self, task_id:int):
        for f in sorted(self.task_dir.rglob("task_*.json"), key=lambda f: f.stem.split("_")[1]):
            task = json.loads(f.read_text(encoding='utf-8'))
            if task["status"] == "pending" :
                newBlockedBy = [x for x in task["blockedBy"] if x != task_id]
                if len(newBlockedBy) != len(task["blockedBy"]):
                    task["blockedBy"] = newBlockedBy
                    self._save(task)
    
    def create(self, subject: str, description: str, blockedBy: list[int]) -> str:
        task = {
            "id": self.next_id, "subject": subject, "description": description,
            "status": "pending", "blockedBy": blockedBy
        }
        self.next_id += 1
        self._save(task)

        return json.dumps(task, indent=2, ensure_ascii=False)

    def update(self, task_id: int, status: str|None, addBlockedBy: list[int]|None, removeBlockedBy: list[int]|None) -> str:
        # find the file and extract task
        task = self._load(task_id)
        if not task:
            return f"<ERROR>Invalid task_id : {task_id}. No such task.</ERROR>"
        # edit it
        if status:
            task["status"] = status
            if status == "completed":
                self._clear_dependency(task_id)
        if addBlockedBy:
            task["blockedBy"] = list(set(task["blockedBy"]+ addBlockedBy))
        if removeBlockedBy:
            task["blockedBy"] = [x for x in task["blockedBy"] if x not in set(removeBlockedBy)]
        # resave
        self._save(task)

        return json.dumps(task, indent=2, ensure_ascii=False)

    def list_all(self) -> str:
        return "\n".join(
            json.dumps(json.loads(f.read_text(encoding='utf-8')), indent=2, ensure_ascii=False) 
                for f in sorted(self.task_dir.rglob("task_*.json"), key=lambda f : int(f.stem.split("_")[1]))
            ) or "No tasks"

    def get(self, task_id: int) -> str:
        return json.dumps(self._load(task_id), indent=2, ensure_ascii=False)
    
    def have_task(self, task_id: int) -> bool:
        task_path = self.task_dir / f"task_{task_id}.json"
        return task_path.exists()
    