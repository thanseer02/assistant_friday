from app.tools.base import BaseTool, PermissionLevel

class CreateReminderTool(BaseTool):
    name = "create_reminder"
    description = "Creates a reminder for the user."
    permission_level = PermissionLevel.WRITE
    parameters = {
        "type": "object",
        "properties": {
            "reminder": {
                "type": "string",
                "description": "What to remind the user about."
            }
        },
        "required": ["reminder"]
    }

    async def execute(self, **kwargs) -> str:
        reminder = kwargs.get("reminder")
        return f"Successfully created reminder: '{reminder}'"
