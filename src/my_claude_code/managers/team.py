from pathlib import Path
import threading
import json

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

    def spawn(self, name: str, role: str, prompt: str) -> str:
        m = self._find_member(name)
        if m:
            if m["status"] not in ["idle", "shutdown"]:
                return f"<ERROR>The agent {name} is {m["status"]}</ERROR>"
            m["status"] = "working"
            m["role"] = role
        else: 
            self.config["members"].append({
                "name": name,
                "role": role,
                "status": "working",
            })
        self._save_config()

        thread = threading.Thread(
            target=self._teammate_loop, args=(name, role, prompt),
            daemon=True
        )
        self.threads[name] = thread
        thread.start()

        return f"Agent {name} is start working as role : {role}"
    
    def _teammate_loop(self, name: str, role: str, prompt: str):
        sys_prompt=f"""
        You are a coding agent at {WORKDIR}. You're a teammate of the lead agent, your name is {name} and your role is {role}.
        Use load_skill to access specialized knowledge before tackling unfamiliar topics.

        Skills available:
        {SKILL_LOADER.get_descriptions()}
        """
        
        messages = [{"role": "user", "content": prompt}]
        BG_teammate = BackgroundManager()
        TODO_teammate = TodoManager()

        turns_since_todo = 0
        for _ in range(50):
            micro_compact(messages)
            if estimate_tokens(messages) >= THRESHOLD:
                messages[:] = auto_compact(messages)
            notifs = BG_teammate.draw_notification()
            if notifs:
                notif_text = "\n".join(
                    f"[bg:{n['task_id']}] {n['status']}: {n['result']}" for n in notifs
                )
                messages.append({"role": "user", "content": f"<background-results>\n{notif_text}\n</background-results>"})
            inbox = BUS.read_inbox(name)
            for msg in inbox:
                messages.append({"role": "user", "content": json.dumps(msg)})
            response = client.messages.create(
                model=MODEL_ID,
                max_tokens=MAX_TOKENS,
                system=sys_prompt,
                tools=self._teammate_tools(),
                messages=messages
            )
            messages.append({'role':'assistant', 'content':response.content})

            tool_uses = [block for block in response.content if block.type == 'tool_use']
            if not tool_uses:
                break
            
            results = []
            manual_compact = False
            shutdown = False
            for block in tool_uses:
                print(bcolors.OKBLUE + block.name + bcolors.ENDC + f"by {name}")
                try:
                    output = self._exec(name, block.name, block.input, BG_teammate, TODO_teammate)
                except Exception as e:
                    output = f"<ERROR>Error executing tool {block.name}: {e}</ERROR>"
                results.append({"type" : "tool_result", "tool_use_id" : block.id, 
                            "content" : output})
                if block.name == "todo":
                    turns_since_todo = -1
                elif block.name == "compact":
                    manual_compact = True
                    compact_focus = block.input.get("focus")
                elif block.name == "shutdown_response" and block.input["approve"] and not str(output).startswith("<ERROR>") :
                    shutdown = True
            if shutdown:
                self._find_member(name)["status"] = "shutdown"
                self._save_config()
                break

            turns_since_todo += 1
            if turns_since_todo > 5:
                results.append({"type": "text", "text": "<reminder>Remember to use the todo tool to manage your tasks!</reminder>"})
            messages.append({"role" : "user", "content" : results})

            if manual_compact:
                messages[:] = auto_compact(messages, compact_focus)
                
        me = self._find_member(name)
        if me and me["status"] != "shutdown":
            me["status"] = "idle"
            self._save_config()

    def _teammate_tools(self):
        return [
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
            {
                "name": "background_run",
                "description": "Run command in background thread. Returns task_id immediately.",
                "input_schema": {"type": "object", "properties": {"command": {"type":"string"}}, "required":["command"], "additionalProperties": False},
            },
            {
                "name": "check_background",
                "description": "Check background task status. Omit task_id to list all.",
                "input_schema": {"type": "object", "properties": {"task_id": {"type":"string"}}, "additionalProperties": False},
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
            {
                "name": "send_message",
                "description": "Send a message to a teammate's inbox.",
                "input_schema": {
                    "type": "object", 
                    "properties": {"to": {"type": "string"}, "content": {"type": "string"}, "msg_type": {"type": "string", "enum": list(VALID_MSG_TYPES)}}, 
                    "required": ["to", "content"],
                    "additionalProperties": False,
                }
            },
            {
                "name": "broadcast", 
                "description": "Send a message to all teammates.",
                "input_schema": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"], "additionalProperties": False}
            },
            {
                "name": "shutdown_response", 
                "description": "Respond to a shutdown request. Approve to shut down, reject to keep working.",
                "input_schema": {"type": "object", "properties": {"request_id": {"type": "string"}, "approve": {"type": "boolean"}, "reason": {"type": "string"}}, "required": ["request_id", "approve"]},
            },
            {
                "name": "plan_request",
                "description": "Submit a plan of your work for lead approval if the work is complex or risky. Provide plan text.",
                "input_schema": {"type": "object", "properties": {"plan": {"type": "string"}}, "required": ["plan"]},
            },
            {
                "name": "request_check",
                "description": "Check the status of a request by request_id",
                "input_schema": {"type": "object", "properties": {"request_id": {"type": "string"}}, "required": ["request_id"], "additionalProperties": False},
            }
        ]
    
    def _exec(self, name: str, tool_name: str, input: dict, BG: BackgroundManager, TODO: TodoManager):
        run = {
            "bash" :            lambda **kwargs : run_bash(kwargs["command"]),
            "read_file" :       lambda **kwargs : run_read(kwargs["path"], kwargs["limit"]),
            "write_file":       lambda **kwargs : run_write(kwargs["path"], kwargs["content"]),
            "edit_file" :       lambda **kwargs : run_edit(kwargs["path"], kwargs["old_text"], kwargs["new_text"]),
            "todo" :            lambda **kwargs : TODO.update(kwargs["items"]),
            "load_skill" :      lambda **kwargs : SKILL_LOADER.get_content(kwargs["name"]),
            "background_run":   lambda **kwargs : BG.run(kwargs["command"]),
            "check_background": lambda **kwargs : BG.check(kwargs.get("task_id")),
            "compact":          lambda **kwargs : "Manual compression requested.",
            "send_message":     lambda **kwargs : BUS.send(name, kwargs["to"], kwargs["content"], kwargs.get("msg_type", "message")),
            "broadcast":        lambda **kwargs : BUS.broadcast(name, kwargs["content"], self.member_names()),
            "shutdown_response":lambda **kwargs : self.handle_shutdown_request(name, kwargs["request_id"], kwargs["approve"], kwargs.get("reason")),
            "plan_request":     lambda **kwargs : self.send_plan_request(name, "lead", kwargs["plan"]),
            "request_check":    lambda **kwargs : self.check_request_status(name, kwargs["request_id"])
        }[tool_name]

        return run(**input) if run else f"Unknown tools: {tool_name}"

    def list_all(self):
        return '\n'.join(json.dumps(m, ensure_ascii=False) for m in self.config["members"]) or "(No team member)"
    
    def member_names(self):
        return [m["name"] for m in self.config["members"]]

    def send_shutdown_request(self, sender: str, to: str) -> str:
        if sender != "lead":
            return f"<ERROR>You have no permission to shutdown teammates.</ERROR>"
        req_id = str(uuid.uuid4())[:8]
        with self._requests_lock:
            self.requests[req_id] = {
                "request_id": req_id,
                "sender": sender, "to": to,
                "type": "shutdown", "status": "pending", 
            }
        BUS.send(sender, to, "Please shut down gracefully.", "shutdown_request", {"request_id": req_id})
        return f"Shutdown request {req_id} sent to '{to}' (status: pending)"

    def handle_shutdown_request(self, handler: str, request_id: str, approve: bool, reason: str=None) -> str:
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
        BUS.send(handler, "lead", f"<Request {request_id} {"Approved" if approve else "Rejected"}>: {reason or "no reason"}", "shutdown_response", {"request_id": request_id})
        return f"Shutdown {'approved' if approve else 'rejected'}"

    def send_plan_request(self, sender: str, to: str, content: str) -> str:
        if sender == "lead":
            return f"Let teammates do their work. Don't plan for them."
        if to != "lead":
            return f"<ERROR>You only need to send plan to the lead.</ERROR>"
        req_id = str(uuid.uuid4())[:8]
        with self._requests_lock:
            self.requests[req_id] = {
                "request_id": req_id,
                "sender": sender, "to": to,
                "type": "plan", "status": "pending", 
            }
        BUS.send(sender, to, f"My plan is: {content}", "plan_request", {"request_id": req_id})
        return f"Plan request {req_id} sent to '{to}' (status: pending)"
    
    def handle_plan_request(self, handler: str, request_id: str, approve: bool, feedback: str=None) -> str:
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
        BUS.send(handler, req["sender"], f"<Request {request_id} {"Approved" if approve else "Rejected"}>: {feedback or "no feedback"}", "plan_response", {"request_id": request_id})
        return f"Plan of {req["sender"]} {'approved' if approve else 'rejected'}"
    
    def check_request_status(self, name: str, request_id: str):
        req = self.requests.get(request_id)
        if not req:
            return f"<ERROR>No such request : {request_id}</ERROR>"
        if name not in [req["sender"], req["to"]]:
            return f"<ERROR>No permission for request {request_id}</ERROR>"
        return json.dumps(req, indent=2, ensure_ascii=False)
