import pytest
import httpx
from fastapi import HTTPException
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.ai_service import AIService
from app.core.config import settings

@pytest.fixture
def ai_service():
    return AIService()

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_generate_response_success(mock_post, ai_service):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"message": {"content": "Test response"}}
    mock_post.return_value = mock_response
    
    history = [{"role": "user", "content": "Test message"}]
    memories = ["favorite color: blue"]
    response = await ai_service.generate_response(history, memories=memories)
    assert response == "Test response"
    
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    # Verify memory was injected
    messages_sent = kwargs["json"]["messages"]
    assert len(messages_sent) == 2
    assert messages_sent[0]["role"] == "system"
    assert "favorite color: blue" in messages_sent[0]["content"]
    assert messages_sent[1]["role"] == "user"
    assert kwargs["json"]["model"] == settings.OLLAMA_MODEL

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_generate_response_with_tool(mock_post, ai_service):
    # First response: AI calls a tool
    mock_response_1 = MagicMock()
    mock_response_1.raise_for_status.return_value = None
    mock_response_1.json.return_value = {
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"function": {"name": "dummy_tool", "arguments": {}}}]
        }
    }
    
    # Second response: AI returns final answer
    mock_response_2 = MagicMock()
    mock_response_2.raise_for_status.return_value = None
    mock_response_2.json.return_value = {"message": {"content": "Final answer"}}
    
    mock_post.side_effect = [mock_response_1, mock_response_2]
    
    # Mock registry
    mock_registry = MagicMock()
    mock_registry.get_ollama_tools.return_value = [{"type": "function", "function": {"name": "dummy_tool"}}]
    mock_registry.execute_tool = AsyncMock(return_value="Tool result")
    
    history = [{"role": "user", "content": "Test message"}]
    response = await ai_service.generate_response(history, tool_registry=mock_registry)
    
    assert response == "Final answer"
    assert mock_post.call_count == 2
    mock_registry.execute_tool.assert_called_once_with("dummy_tool", {})

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_generate_response_timeout(mock_post, ai_service):
    mock_post.side_effect = httpx.TimeoutException("Timeout")
    
    history = [{"role": "user", "content": "Test message"}]
    with pytest.raises(HTTPException) as excinfo:
        await ai_service.generate_response(history)
        
    assert excinfo.value.status_code == 504
    assert excinfo.value.detail == "AI engine response timeout"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_generate_response_unavailable(mock_post, ai_service):
    mock_post.side_effect = httpx.RequestError("Connection Error")
    
    history = [{"role": "user", "content": "Test message"}]
    with pytest.raises(HTTPException) as excinfo:
        await ai_service.generate_response(history)
        
    assert excinfo.value.status_code == 503
    assert excinfo.value.detail == "AI engine is currently unavailable"
