import datetime
import platform
from .base import BaseTool

class SystemTimeTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_time"

    @property
    def description(self) -> str:
        return "Gets the current local time."

    @property
    def parameters_schema(self) -> dict:
        return {}

    def execute(self, **kwargs) -> str:
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}."

class SystemDateTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_date"

    @property
    def description(self) -> str:
        return "Gets the current local date."

    @property
    def parameters_schema(self) -> dict:
        return {}

    def execute(self, **kwargs) -> str:
        today = datetime.date.today()
        return f"Today's date is {today.strftime('%B %d, %Y')}."

class SystemOsTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_os"

    @property
    def description(self) -> str:
        return "Detects the operating system the assistant is running on."

    @property
    def parameters_schema(self) -> dict:
        return {}

    def execute(self, **kwargs) -> str:
        os_name = platform.system()
        if os_name == "Darwin":
            return "You are running macOS."
        elif os_name == "Windows":
            return "You are running Windows."
        return f"You are running {os_name}."
