from pathlib import Path
import threading
import json
import uuid

from my_claude_code.managers.message_bus import MessageBus
from my_claude_code.managers.registry import get_managers

class TeamManager:
    def __init__(self, team_dir: Path):
        self.dir = team_dir
        self.dir.mkdir(exist_ok=True)
        self.config_path = self.dir / "config.json"
        self.config = self._load_config()
        self._save_config()
        self.threads = {}
        self.requests = {}
        self._requests_lock = threading.Lock()

    def _load_config(self) -> dict:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text(encoding='utf-8'))
        
        return {"team_name": "default", "members": []}

    def _save_config(self):
        self.config_path.write_text(json.dumps(self.config, indent=2))

    def _find_member(self, name: str) -> dict:
        for m in self.config["members"]:
            if m["name"] == name:
                return m
        return None

    def spawn(self, name: str, prompt: str, model_id: str, work_dir: Path, bus: MessageBus) -> str:
        m = self._find_member(name)
        if m:
            if m["status"] not in ["idle", "shutdown"]:
                return f"<ERROR>The agent {name} is {m["status"]}</ERROR>"
            m["status"] = "working"
        else: 
            self.config["members"].append({
                "name": name,
                "role": "teammate",
                "status": "working",
            })
        self._save_config()

        thread = threading.Thread(
            target=self._teammate_loop, args=(name, prompt, model_id, work_dir, bus),
            daemon=True
        )
        self.threads[name] = thread
        thread.start()

        return f"Teammate {name} is start working"
    
    def _teammate_loop(self, name: str, prompt: str, model_id: str, work_dir: Path, bus: MessageBus):
        from my_claude_code.runtime import create_runtime
        teammate = create_runtime(name, role="teammate", model_id=model_id, workdir=work_dir,
                                  managers=get_managers("teammate"))
        teammate.bus = bus
        teammate.team = self
        teammate.history.append({"role": "user", "content": prompt})
        while True:
            me = self._find_member(name)
            if not me or me["status"] != "working":
                break
            teammate.agent_loop()

            me = self._find_member(name)
            if me and me["status"] != "shutdown":
                me["status"] = "idle"
                self._save_config()

    def list_all(self):
        return '\n'.join(json.dumps(m, ensure_ascii=False) for m in self.config["members"]) or "(No team member)"
    
    def member_names(self):
        return [m["name"] for m in self.config["members"]]

    def send_shutdown_request(self, bus: MessageBus, sender: str, to: str) -> str:
        from my_claude_code.config import MAIN_NAME
        if sender != MAIN_NAME:
            return f"<ERROR>You have no permission to shutdown teammates.</ERROR>"
        req_id = str(uuid.uuid4())[:8]
        with self._requests_lock:
            self.requests[req_id] = {
                "request_id": req_id,
                "sender": sender, "to": to,
                "type": "shutdown", "status": "pending", 
            }
        bus.send(sender, to, "Please shut down gracefully.", "shutdown_request", {"request_id": req_id})
        return f"Shutdown request {req_id} sent to '{to}' (status: pending)"

    def handle_shutdown_request(self, bus: MessageBus, handler: str, request_id: str, approve: bool, reason: str=None) -> str:
        req = self.requests.get(request_id)
        if not req:
            return f"<ERROR>No such request : {request_id}</ERROR>"
        if req["to"] != handler:
            return f"<ERROR>You can't handle shutdown for your teammate</ERROR>"
        if req["type"] != "shutdown" or req["status"] != "pending":
            return f"<ERROR>request {request_id} is not a shutdown request or it has been handled.</ERROR>"
        with self._requests_lock:
            req["status"] = "completed"
            req["result"] = "Approved" if approve else "Rejected"
        bus.send(handler, "lead", f"<Request {request_id} {"Approved" if approve else "Rejected"}>: {reason or "no reason"}", "shutdown_response", {"request_id": request_id})
        return f"Shutdown {'approved' if approve else 'rejected'}"

    def send_plan_request(self, bus: MessageBus, sender: str, to: str, content: str) -> str:
        from my_claude_code.config import MAIN_NAME
        if sender == MAIN_NAME:
            return f"Let teammates do their work. Don't plan for them."
        if to != MAIN_NAME:
            return f"<ERROR>You only need to send plan to the lead.</ERROR>"
        req_id = str(uuid.uuid4())[:8]
        with self._requests_lock:
            self.requests[req_id] = {
                "request_id": req_id,
                "sender": sender, "to": to,
                "type": "plan", "status": "pending", 
            }
        bus.send(sender, to, f"My plan is: {content}", "plan_request", {"request_id": req_id})
        return f"Plan request {req_id} sent to '{to}' (status: pending)"
    
    def handle_plan_request(self, bus: MessageBus, handler: str, request_id: str, approve: bool, feedback: str=None) -> str:
        req = self.requests.get(request_id)
        if not req:
            return f"<ERROR>No such request : {request_id}</ERROR>"
        if req["to"] != handler:
            return f"<ERROR>You can't handle plan for your teammate</ERROR>"
        if req["type"] != "plan" or req["status"] != "pending":
            return f"<ERROR>request {request_id} is not a plan request or it has been handled.</ERROR>"
        with self._requests_lock:
            req["status"] = "completed"
            req["result"] = "Approved" if approve else "Rejected"
        bus.send(handler, req["sender"], f"<Request {request_id} {"Approved" if approve else "Rejected"}>: {feedback or "no feedback"}", "plan_response", {"request_id": request_id})
        return f"Plan of {req["sender"]} {'approved' if approve else 'rejected'}"
    
    def check_request_status(self, name: str, request_id: str):
        req = self.requests.get(request_id)
        if not req:
            return f"<ERROR>No such request : {request_id}</ERROR>"
        if name not in [req["sender"], req["to"]]:
            return f"<ERROR>No permission for request {request_id}</ERROR>"
        return json.dumps(req, indent=2, ensure_ascii=False)
