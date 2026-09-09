import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch, AsyncMock
from app.main import app

@pytest.fixture
def mock_adapter():
    with patch("app.api.telegram.TelegramAdapter") as mock:
        instance = mock.return_value
        
        mock_msg = MagicMock()
        mock_msg.conversation_id = "tg_chat_1"
        mock_msg.text = "Hello"
        mock_msg.metadata = {"telegram_chat_id": "1"}
        
        instance.parse_update.return_value = mock_msg
        instance.send_message = AsyncMock(return_value=True)
        yield instance

@pytest.fixture
def mock_ai_service_tg():
    with patch("app.api.telegram.AIService") as mock:
        instance = mock.return_value
        instance.generate_response = AsyncMock(return_value="AI Reply")
        instance.extract_memories = AsyncMock(return_value=[])
        yield instance

@pytest.fixture
def mock_conversation_service_tg():
    with patch("app.api.telegram.ConversationService") as mock:
        instance = mock.return_value
        mock_conv = MagicMock()
        mock_conv.id = "tg_chat_1"
        instance.get_or_create_conversation.return_value = mock_conv
        yield instance

@pytest.fixture
def mock_memory_service_tg():
    with patch("app.api.telegram.MemoryService") as mock:
        instance = mock.return_value
        instance.search_memories.return_value = []
        yield instance

@pytest.mark.asyncio
async def test_telegram_webhook_valid(mock_adapter, mock_ai_service_tg, mock_conversation_service_tg, mock_memory_service_tg):
    payload = {"update_id": 1, "message": {"text": "Hello", "chat": {"id": 1}}}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/webhooks/telegram", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
    mock_adapter.parse_update.assert_called_once_with(payload)
    mock_ai_service_tg.generate_response.assert_called_once()
    # Note: send_message is called as a background task, so we can't easily assert it here without waiting for the task
    # We just ensure the endpoint returns 200

@pytest.mark.asyncio
async def test_telegram_webhook_duplicate(mock_adapter):
    mock_adapter.parse_update.return_value = None
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/webhooks/telegram", json={})
        
    assert response.status_code == 200
    assert response.json() == {"status": "ignored or duplicate"}
