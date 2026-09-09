import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.services.ai_service import AIService

@pytest.fixture
def mock_ai_service():
    with patch("app.api.chat.AIService") as mock:
        instance = mock.return_value
        instance.generate_response = AsyncMock(return_value="Hello! How can I help?")
        yield instance

@pytest.mark.asyncio
async def test_chat_endpoint(mock_ai_service):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/chat", json={"message": "Hello"})
    
    assert response.status_code == 200
    assert response.json() == {"response": "Hello! How can I help?"}
    mock_ai_service.generate_response.assert_called_once_with("Hello")
