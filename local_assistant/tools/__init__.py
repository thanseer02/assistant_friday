from .base import BaseTool
from .registry import ToolRegistry
from .calculator import CalculatorTool
from .system import SystemTimeTool, SystemDateTool, SystemOsTool
from .files import CreateFolderTool, ListFilesTool, CheckExistsTool
from .apps import OpenAppTool
from .memory_tool import RememberTool, RecallTool, ForgetTool, ListMemoriesTool

def get_default_registry() -> ToolRegistry:
    """Returns a pre-configured ToolRegistry loaded with all default tools."""
    registry = ToolRegistry()
    
    registry.register(CalculatorTool())
    
    registry.register(SystemTimeTool())
    registry.register(SystemDateTool())
    registry.register(SystemOsTool())
    
    registry.register(CreateFolderTool())
    registry.register(ListFilesTool())
    registry.register(CheckExistsTool())
    
    registry.register(OpenAppTool())
    
    registry.register(RememberTool())
    registry.register(RecallTool())
    registry.register(ForgetTool())
    registry.register(ListMemoriesTool())
    
    return registry

__all__ = ["BaseTool", "ToolRegistry", "get_default_registry"]
