from typing import Dict, Any
from .base import BaseTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """Registers a tool to make it available to the assistant."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name)

    def get_all_tools_metadata(self) -> str:
        """
        Dynamically generates a string describing all registered tools.
        This is injected into the LLM system prompt so the AI knows what it can do.
        """
        metadata = []
        for name, tool in self._tools.items():
            schema_str = ", ".join(f'"{k}": <{v}>' for k, v in tool.parameters_schema.items())
            if not schema_str:
                schema_str = "None"
            else:
                schema_str = f"{{{schema_str}}}"
            metadata.append(f"- Tool: '{name}' | Description: {tool.description} | JSON Parameters: {schema_str}")
        
        # Add fallback unknown tool
        metadata.append("- Tool: 'unknown' | Description: Use this if the user says hello or asks something you can't do. | JSON Parameters: None")
        
        metadata.append("- Tool: 'help' | Description: Use this if the user asks for help or wants a list of things you can do. | JSON Parameters: None")
        
        return "\n".join(metadata)

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Safely executes a tool after validating its existence and parameters."""
        if tool_name == "help":
            help_text = "Here is a list of things I can do:\n"
            for name, tool_obj in self._tools.items():
                help_text += f"- {name}: {tool_obj.description}\n"
            return help_text.strip()
            
        if tool_name == "unknown":
            return "I am a local assistant. How can I help you? (Type 'help' for a list of things I can do)"
            
        tool = self.get_tool(tool_name)
        if not tool:
            return f"[System Guard] Error: The LLM attempted to call an unregistered tool '{tool_name}'."
            
        # Strict validation
        missing_params = [p for p in tool.parameters_schema.keys() if p not in parameters]
        if missing_params:
            return f"[System Guard] Error: Missing required parameters for '{tool_name}': {', '.join(missing_params)}"
            
        try:
            return tool.execute(**parameters)
        except Exception as e:
            return f"[System Guard] Error executing '{tool_name}': {str(e)}"
