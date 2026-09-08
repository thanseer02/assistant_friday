import datetime
import platform

class SystemTool:
    def get_time(self) -> str:
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}."
        
    def get_date(self) -> str:
        today = datetime.date.today()
        return f"Today's date is {today.strftime('%B %d, %Y')}."
        
    def get_os(self) -> str:
        os_name = platform.system()
        if os_name == "Darwin":
            return "macOS"
        elif os_name == "Windows":
            return "Windows"
        return os_name
