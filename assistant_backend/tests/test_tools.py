import pytest
from app.tools.registry import ToolRegistry
from app.tools.base import BaseTool

class DummyTool(BaseTool):
    name = "dummy_tool"
    description = "A dummy tool"
    parameters = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> str:
        if kwargs.get("fail"):
            raise ValueError("Intentional failure")
        return "Success"

class InvalidParamTool(BaseTool):
    name = "invalid_param_tool"
    description = "Tool with specific params"
    parameters = {"type": "object", "properties": {"val": {"type": "integer"}}, "required": ["val"]}

    async def execute(self, **kwargs) -> str:
        # Assuming AI gives wrong param type, we just demonstrate handling
        val = kwargs.get("val")
        if not isinstance(val, int):
            raise TypeError("Expected integer")
        return f"Got {val}"

@pytest.fixture
def registry():
    r = ToolRegistry()
    r.register(DummyTool())
    r.register(InvalidParamTool())
    return r

def test_tool_registration(registry):
    tools = registry.list_tools()
    assert len(tools) == 2
    
    ollama_tools = registry.get_ollama_tools()
    assert len(ollama_tools) == 2
    assert ollama_tools[0]["function"]["name"] == "dummy_tool"

@pytest.mark.asyncio
async def test_valid_tool_execution(registry):
    result = await registry.execute_tool("dummy_tool", {})
    assert result == "Success"

@pytest.mark.asyncio
async def test_invalid_tool(registry):
    result = await registry.execute_tool("nonexistent_tool", {})
    assert "Error: Tool 'nonexistent_tool' is not registered." in result

@pytest.mark.asyncio
async def test_invalid_parameters(registry):
    result = await registry.execute_tool("invalid_param_tool", {"val": "string_instead_of_int"})
    assert "Error: Execution failed. Expected integer" in result

@pytest.mark.asyncio
async def test_tool_execution_failure(registry):
    result = await registry.execute_tool("dummy_tool", {"fail": True})
    assert "Error: Execution failed. Intentional failure" in result
