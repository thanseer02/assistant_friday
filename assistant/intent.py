from enum import Enum, auto
from dataclasses import dataclass

class Intent(Enum):
    GET_TIME = auto()
    GET_DATE = auto()
    GET_OS = auto()
    CALCULATE = auto()
    OPEN_APP = auto()
    CREATE_FOLDER = auto()
    LIST_FILES = auto()
    CHECK_EXISTS = auto()
    GREETING = auto()
    HELP = auto()
    EXIT = auto()
    UNKNOWN = auto()

@dataclass
class ParsedIntent:
    intent: Intent
    raw_input: str
    entities: dict

class IntentParser:
    def parse(self, user_input: str) -> ParsedIntent:
        normalized = user_input.strip().lower()
        entities = {}
        
        if not normalized:
            return ParsedIntent(Intent.UNKNOWN, user_input, entities)
            
        if normalized in ["hello", "hi"]:
            return ParsedIntent(Intent.GREETING, user_input, entities)
            
        if normalized == "help":
            return ParsedIntent(Intent.HELP, user_input, entities)
            
        if normalized in ["exit", "quit"]:
            return ParsedIntent(Intent.EXIT, user_input, entities)
            
        if "time" in normalized:
            return ParsedIntent(Intent.GET_TIME, user_input, entities)
            
        if "date" in normalized:
            return ParsedIntent(Intent.GET_DATE, user_input, entities)
            
        if "os" in normalized or "windows or mac" in normalized:
            return ParsedIntent(Intent.GET_OS, user_input, entities)
            
        if "calculate" in normalized:
            expression = normalized.replace("calculate", "").strip()
            entities["expression"] = expression
            return ParsedIntent(Intent.CALCULATE, user_input, entities)
            
        if "open" in normalized:
            app_name = normalized.replace("open", "").strip()
            entities["app_name"] = app_name
            return ParsedIntent(Intent.OPEN_APP, user_input, entities)
            
        if "create a folder called" in normalized:
            folder_name = normalized.replace("create a folder called", "").strip()
            entities["folder_name"] = folder_name
            return ParsedIntent(Intent.CREATE_FOLDER, user_input, entities)
            
        if "list files" in normalized:
            return ParsedIntent(Intent.LIST_FILES, user_input, entities)
            
        if "check if" in normalized and "exists" in normalized:
            path = normalized.replace("check if", "").replace("exists", "").strip()
            entities["path"] = path
            return ParsedIntent(Intent.CHECK_EXISTS, user_input, entities)
            
        return ParsedIntent(Intent.UNKNOWN, user_input, entities)
