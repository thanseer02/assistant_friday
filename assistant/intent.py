import json
from enum import Enum, auto
from dataclasses import dataclass
from ai.model import LanguageModel

class Intent(Enum):
    GET_TIME = auto()
    GET_DATE = auto()
    GET_OS = auto()
    CALCULATE = auto()
    OPEN_APP = auto()
    CREATE_FOLDER = auto()
    LIST_FILES = auto()
    CHECK_EXISTS = auto()
    REMEMBER = auto()
    RECALL = auto()
    FORGET = auto()
    LIST_MEMORIES = auto()
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
    """
    Uses a Local LLM to parse natural language into a structured ParsedIntent.
    """
    def __init__(self, llm: LanguageModel):
        self.llm = llm

    def parse(self, user_input: str) -> ParsedIntent:
        normalized = user_input.strip()
        if not normalized:
            return ParsedIntent(Intent.UNKNOWN, user_input, {})

        # System prompt instructing the LLM to output valid JSON matching our schema
        prompt = f"""
You are an intent parser for a local assistant.
Convert the user's input into a JSON object with exactly two keys: "intent" and "entities".
Do not output any markdown formatting, backticks, or other text. ONLY valid JSON.

Valid intents are:
- GET_TIME (entities: empty)
- GET_DATE (entities: empty)
- GET_OS (entities: empty)
- CALCULATE (entities: "expression")
- OPEN_APP (entities: "app_name")
- CREATE_FOLDER (entities: "folder_name")
- LIST_FILES (entities: empty)
- CHECK_EXISTS (entities: "path")
- REMEMBER (entities: "key", "value")
- RECALL (entities: "key")
- FORGET (entities: "key")
- LIST_MEMORIES (entities: empty)
- GREETING (entities: empty)
- HELP (entities: empty)
- EXIT (entities: empty)
- UNKNOWN (if it matches none of the above)

User input: {user_input}
"""
        try:
            llm_response = self.llm.generate(prompt)
            
            # Clean up the response in case the LLM ignored instructions and used markdown
            clean_response = llm_response.replace('```json', '').replace('```', '').strip()
            
            parsed_data = json.loads(clean_response)
            
            intent_str = parsed_data.get("intent", "UNKNOWN").upper()
            entities = parsed_data.get("entities", {})
            
            # Strict validation against our allowlist
            try:
                intent = Intent[intent_str]
            except KeyError:
                intent = Intent.UNKNOWN
                
            return ParsedIntent(intent, user_input, entities)
            
        except json.JSONDecodeError:
            # Safe fallback if the LLM hallucinated invalid JSON
            return ParsedIntent(Intent.UNKNOWN, user_input, {})
        except Exception as e:
            print(f"[System] Parser Error: {e}")
            return ParsedIntent(Intent.UNKNOWN, user_input, {})
