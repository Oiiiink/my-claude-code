import time
import json

class MessageBus:
    def __init__(self, inbox_dir: Path):
        self.inbox = inbox_dir
        self.inbox.mkdir(exist_ok=True)

    def send(self, sender: str, to:str, content: str, msg_type: str = "message", extra: dict = None) -> str:
        if msg_type not in VALID_MSG_TYPES:
            return f"<ERROR>Invalid message type: {msg_type}. Valid type: {str(VALID_MSG_TYPES)}</ERROR>"
        
        msg = {
            "from": sender,
            "content": content,
            "type": msg_type,
            "timestamp": time.time(),
        }
        msg["metadata"] = extra or {}
        inbox_path = self.inbox / f"{to}.jsonl"
        with open(inbox_path, "a", encoding='utf-8') as f:
            f.write(json.dumps(msg) + '\n')
        
        return f"Successfully send message from {sender} to {to}, the content is {content[:80]}"

    def read_inbox(self, name: str) -> list:
        inbox_path = self.inbox / f"{name}.jsonl"
        if not inbox_path.exists():
            return []
        
        messages = []
        for raw_line in inbox_path.read_text().splitlines():
            line = raw_line.strip()
            if line:
                messages.append(json.loads(line))
        inbox_path.write_text("")
        return messages

    def broadcast(self, sender: str, content: str, teammates: list) -> str:
        count = 0
        for name in teammates:
            if name != sender:
                self.send(sender, name, content, "broadcast")
                count += 1
        return f"Broadcast to {count} teammates"
    