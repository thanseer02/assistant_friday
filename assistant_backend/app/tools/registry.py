import logging
from typing import Any
from app.tools.base import BaseTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        if tool.name in self._tools:
            logger.warning(f"Tool {tool.name} is already registered. Overwriting.")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_ollama_tools(self) -> list[dict[str, Any]]:
        return [tool.to_ollama_format() for tool in self._tools.values()]

    async def execute_tool(self, name: str, kwargs: dict[str, Any]) -> str:
        tool = self.get_tool(name)
        if not tool:
            return f"Error: Tool '{name}' is not registered."
        
        try:
            result = await tool.execute(**kwargs)
            return str(result)
        except Exception as e:
            logger.error(f"Error executing tool '{name}': {e}")
            return f"Error: Execution failed. {str(e)}"
