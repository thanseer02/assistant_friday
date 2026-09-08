from .database import DatabaseManager

class MemoryTool:
    """
    A tool used by the assistant to interact with the database.
    It formats the raw database results into natural language responses.
    """
    def __init__(self):
        self.db = DatabaseManager()

    def remember(self, key: str, value: str) -> str:
        if not key or not value:
            return "Please tell me both what to remember and what its value is."
        self.db.set_memory(key, value)
        return f"Got it. I'll remember that your {key} is {value}."

    def recall(self, key: str) -> str:
        if not key:
            return "What would you like me to recall?"
        value = self.db.get_memory(key)
        if value:
            return f"Your {key} is {value}."
        return f"I don't remember anything about your '{key}'."

    def forget(self, key: str) -> str:
        if not key:
            return "What would you like me to forget?"
        success = self.db.delete_memory(key)
        if success:
            return f"I have forgotten about your {key}."
        return f"I don't have any memory of your '{key}' to forget."

    def list_all(self) -> str:
        memories = self.db.list_memories()
        if not memories:
            return "I don't have any memories stored."
        lines = ["Here is what I currently remember about you:"]
        for k, v in memories.items():
            lines.append(f"  - {k}: {v}")
        return "\n".join(lines)
