from .intent import Intent, ParsedIntent
from commands.calculator import CalculatorTool
from commands.system import SystemTool
from commands.files import FilesTool
from commands.apps import AppsTool
from memory.memory import MemoryTool

class CommandRouter:
    def __init__(self):
        # Initialize the actual tool implementations
        self.calculator = CalculatorTool()
        self.system = SystemTool()
        self.files = FilesTool()
        self.apps = AppsTool()
        self.memory = MemoryTool()

    def route(self, parsed_intent: ParsedIntent) -> str:
        intent = parsed_intent.intent
        entities = parsed_intent.entities
        
        if intent == Intent.GREETING:
            return "Hello! How can I help you today?"
            
        if intent == Intent.HELP:
            return (
                "Available commands:\n"
                "  - hello / hi\n"
                "  - what time is it\n"
                "  - tell me the date\n"
                "  - what is my os\n"
                "  - calculate [expression] (e.g., calculate 25 * 10)\n"
                "  - open [app] (e.g., open calculator)\n"
                "  - create a folder called [name]\n"
                "  - list files\n"
                "  - check if [path] exists\n"
                "  - remember that my [key] is [value] (e.g., remember that my favorite editor is VS Code)\n"
                "  - what is my [key]? (e.g., what is my favorite editor?)\n"
                "  - forget my [key]\n"
                "  - list memories\n"
                "  - help\n"
                "  - exit / quit"
            )
            
        if intent == Intent.EXIT:
            return "Goodbye! Have a great day!"
            
        if intent == Intent.GET_TIME:
            return self.system.get_time()
            
        if intent == Intent.GET_DATE:
            return self.system.get_date()
            
        if intent == Intent.GET_OS:
            return f"You are running {self.system.get_os()}."
            
        if intent == Intent.CALCULATE:
            expression = entities.get("expression", "")
            if not expression:
                return "Please provide an expression to calculate."
            result = self.calculator.evaluate(expression)
            return f"Result: {result}"
                
        if intent == Intent.OPEN_APP:
            app_name = entities.get("app_name", "")
            if not app_name:
                return "Please specify an app to open."
            return self.apps.open_app(app_name)
            
        if intent == Intent.CREATE_FOLDER:
            folder_name = entities.get("folder_name", "")
            if not folder_name:
                return "Please specify a folder name."
            return self.files.create_folder(folder_name)
            
        if intent == Intent.LIST_FILES:
            return self.files.list_files()
            
        if intent == Intent.CHECK_EXISTS:
            path = entities.get("path", "")
            if not path:
                return "Please specify a path to check."
            return self.files.check_exists(path)
            
        if intent == Intent.REMEMBER:
            key = entities.get("key", "")
            value = entities.get("value", "")
            return self.memory.remember(key, value)
            
        if intent == Intent.RECALL:
            key = entities.get("key", "")
            return self.memory.recall(key)
            
        if intent == Intent.FORGET:
            key = entities.get("key", "")
            return self.memory.forget(key)
            
        if intent == Intent.LIST_MEMORIES:
            return self.memory.list_all()
            
        return f"I don't understand '{parsed_intent.raw_input}'. Type 'help' for examples."
