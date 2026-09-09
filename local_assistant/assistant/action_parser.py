import json
from dataclasses import dataclass
from ai.model import LanguageModel
from tools.registry import ToolRegistry

@dataclass
class ParsedAction:
    tool_name: str
    parameters: dict
    raw_input: str

class ActionParser:
    """
    Uses a Local LLM to parse natural language into a structured Tool Action.
    It dynamically queries the ToolRegistry to know what tools exist.
    """
    def __init__(self, llm: LanguageModel, registry: ToolRegistry):
        self.llm = llm
        self.registry = registry

    def parse(self, user_input: str) -> ParsedAction:
        normalized = user_input.strip()
        if not normalized:
            return ParsedAction("unknown", {}, user_input)

        # Dynamically fetch available tools
        available_tools = self.registry.get_all_tools_metadata()

        # System prompt instructing the LLM
        prompt = f"""
You are the brain of a local AI assistant. 
Your job is to read the user's input and decide which tool to execute.
You must output ONLY a valid JSON object with exactly two keys: "tool" and "parameters".
Do not output any conversational text, markdown formatting, or backticks.

Here are the tools currently registered in the system:
{available_tools}

User input: {user_input}
"""
        try:
            llm_response = self.llm.generate(prompt)
            clean_response = llm_response.replace('```json', '').replace('```', '').strip()
            
            parsed_data = json.loads(clean_response)
            
            tool_name = parsed_data.get("tool", "unknown").lower()
            parameters = parsed_data.get("parameters", {})
            
            return ParsedAction(tool_name, parameters, user_input)
            
        except json.JSONDecodeError:
            print("[System Guard] LLM hallucinated invalid JSON.")
            return ParsedAction("unknown", {}, user_input)
        except Exception as e:
            print(f"[System Error] Parser Error: {e}")
            return ParsedAction("unknown", {}, user_input)
