import subprocess
import platform

class AppsTool:
    def __init__(self):
        self.os_name = platform.system()
        
        # Predefined safe mappings to avoid arbitrary execution
        self.app_mappings = {
            "calculator": {
                "Windows": "calc.exe",
                "Darwin": "Calculator"
            },
            "notepad": {
                "Windows": "notepad.exe",
                "Darwin": "TextEdit"
            },
            "browser": {
                # Simple fallback for default browser
                "Windows": "explorer.exe",
                "Darwin": "Safari"
            }
        }
        
    def open_app(self, app_name: str) -> str:
        app_name = app_name.lower().strip()
        
        if app_name not in self.app_mappings:
            return f"Security Error: Application '{app_name}' is not in the allowed list (calculator, notepad, browser)."
            
        target = self.app_mappings[app_name].get(self.os_name)
        
        if not target:
            return f"I don't know how to open '{app_name}' on {self.os_name}."
            
        try:
            if self.os_name == "Darwin":
                # Secure execution on macOS
                subprocess.Popen(["open", "-a", target])
            elif self.os_name == "Windows":
                # Secure execution on Windows
                subprocess.Popen([target])
            return f"Successfully opened {app_name}."
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"
