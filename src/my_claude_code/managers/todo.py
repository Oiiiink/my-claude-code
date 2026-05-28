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