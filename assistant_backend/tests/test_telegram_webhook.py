import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch, AsyncMock
from app.main import app
from app.schemas.integration import OutgoingMessage

@pytest.fixture
def mock_adapter():
    with patch("app.api.telegram.TelegramAdapter") as mock:
        instance = mock.return_value
        
        mock_msg = MagicMock()
        mock_msg.conversation_id = "tg_chat_1"
        mock_msg.text = "Hello"
        mock_msg.metadata = {"telegram_chat_id": "1"}
        
        instance.receive_message = AsyncMock(return_value=mock_msg)
        instance.send_message = AsyncMock(return_value=True)
        yield instance

@pytest.fixture
def mock_processor():
    with patch("app.api.telegram.process_incoming_message") as mock:
        outgoing = OutgoingMessage(
            platform="telegram",
            platform_user_id="user1",
            conversation_id="tg_chat_1",
            text="Processed Reply"
        )
        mock.return_value = outgoing
        yield mock

@pytest.mark.asyncio
async def test_telegram_webhook_valid(mock_adapter, mock_processor):
    payload = {"update_id": 1, "message": {"text": "Hello", "chat": {"id": 1}}}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/webhooks/telegram", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
    mock_adapter.receive_message.assert_called_once_with(payload)
    mock_processor.assert_called_once()
    # Note: background_send_message and extract_memories are fired into BackgroundTasks.

@pytest.mark.asyncio
async def test_telegram_webhook_duplicate(mock_adapter):
    mock_adapter.receive_message = AsyncMock(return_value=None)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/webhooks/telegram", json={})
        
    assert response.status_code == 200
    assert response.json() == {"status": "ignored or duplicate"}
