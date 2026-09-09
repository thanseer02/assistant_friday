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
    mock_response.json.return_value = {"response": "Test response"}
    mock_post.return_value = mock_response
    
    response = await ai_service.generate_response("Test message")
    assert response == "Test response"
    
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["prompt"] == "Test message"
    assert kwargs["json"]["model"] == settings.OLLAMA_MODEL

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_generate_response_timeout(mock_post, ai_service):
    mock_post.side_effect = httpx.TimeoutException("Timeout")
    
    with pytest.raises(HTTPException) as excinfo:
        await ai_service.generate_response("Test message")
        
    assert excinfo.value.status_code == 504
    assert excinfo.value.detail == "AI engine response timeout"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_generate_response_unavailable(mock_post, ai_service):
    mock_post.side_effect = httpx.RequestError("Connection Error")
    
    with pytest.raises(HTTPException) as excinfo:
        await ai_service.generate_response("Test message")
        
    assert excinfo.value.status_code == 503
    assert excinfo.value.detail == "AI engine is currently unavailable"
