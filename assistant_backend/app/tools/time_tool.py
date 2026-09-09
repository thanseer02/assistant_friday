from datetime import datetime
import pytz
from app.tools.base import BaseTool

class GetCurrentTimeTool(BaseTool):
    name = "get_current_time"
    description = "Get the current time for a specific timezone (e.g., 'UTC', 'America/New_York'). If timezone is not provided, returns UTC time."
    parameters = {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "The timezone to get the current time for. Defaults to UTC."
            }
        },
        "required": []
    }

    async def execute(self, **kwargs) -> str:
        tz_string = kwargs.get("timezone", "UTC")
        try:
            tz = pytz.timezone(tz_string)
            current_time = datetime.now(tz)
            return f"The current time in {tz_string} is {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}."
        except pytz.UnknownTimeZoneError:
            return f"Error: Unknown timezone '{tz_string}'."
