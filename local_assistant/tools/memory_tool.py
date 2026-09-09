from memory.database import DatabaseManager
from .base import BaseTool

class RememberTool(BaseTool):
    @property
    def name(self) -> str:
        return "remember"

    @property
    def description(self) -> str:
        return "Saves a user preference or memory (e.g. key: 'favorite color', value: 'blue')."

    @property
    def parameters_schema(self) -> dict:
        return {"key": "string", "value": "string"}

    def __init__(self):
        self.db = DatabaseManager()

    def execute(self, key: str = "", value: str = "", **kwargs) -> str:
        if not key or not value:
            return "Please provide both a key and a value."
        self.db.set_memory(key, value)
        return f"Got it. I'll remember that your {key} is {value}."

class RecallTool(BaseTool):
    @property
    def name(self) -> str:
        return "recall"

    @property
    def description(self) -> str:
        return "Retrieves a saved user preference by its key."

    @property
    def parameters_schema(self) -> dict:
        return {"key": "string"}

    def __init__(self):
        self.db = DatabaseManager()

    def execute(self, key: str = "", **kwargs) -> str:
        if not key:
            return "Please specify what you want me to recall."
        value = self.db.get_memory(key)
        if value:
            return f"Your {key} is {value}."
        return f"I don't remember anything about your '{key}'."

class ForgetTool(BaseTool):
    @property
    def name(self) -> str:
        return "forget"

    @property
    def description(self) -> str:
        return "Deletes a saved user preference by its key."

    @property
    def parameters_schema(self) -> dict:
        return {"key": "string"}

    def __init__(self):
        self.db = DatabaseManager()

    def execute(self, key: str = "", **kwargs) -> str:
        if not key:
            return "Please specify what you want me to forget."
        success = self.db.delete_memory(key)
        if success:
            return f"I have forgotten about your {key}."
        return f"I don't have any memory of your '{key}' to forget."

class ListMemoriesTool(BaseTool):
    @property
    def name(self) -> str:
        return "list_memories"

    @property
    def description(self) -> str:
        return "Lists all saved user preferences and memories."

    @property
    def parameters_schema(self) -> dict:
        return {}

    def __init__(self):
        self.db = DatabaseManager()

    def execute(self, **kwargs) -> str:
        memories = self.db.list_memories()
        if not memories:
            return "I don't have any memories stored."
        lines = ["Here is what I currently remember about you:"]
        for k, v in memories.items():
            lines.append(f"  - {k}: {v}")
        return "\n".join(lines)
