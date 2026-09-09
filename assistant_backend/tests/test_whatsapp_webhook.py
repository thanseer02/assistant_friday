import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch, AsyncMock
from app.main import app
from app.schemas.integration import OutgoingMessage

@pytest.fixture
def mock_adapter():
    with patch("app.api.whatsapp.WhatsAppAdapter") as mock:
        instance = mock.return_value
        
        mock_msg = MagicMock()
        mock_msg.conversation_id = "wa_chat_1"
        mock_msg.text = "Hello"
        mock_msg.metadata = {"whatsapp_wamid": "wamid_1"}
        
        instance.receive_message = AsyncMock(return_value=mock_msg)
        instance.send_message = AsyncMock(return_value=True)
        yield instance

@pytest.fixture
def mock_processor():
    with patch("app.api.whatsapp.process_incoming_message") as mock:
        outgoing = OutgoingMessage(
            platform="whatsapp",
            platform_user_id="user1",
            conversation_id="wa_chat_1",
            text="Processed Reply"
        )
        mock.return_value = outgoing
        yield mock

@pytest.mark.asyncio
async def test_whatsapp_verify_webhook_valid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Mocking settings to ensure the token matches
        with patch("app.api.whatsapp.settings") as mock_settings:
            mock_settings.WHATSAPP_VERIFY_TOKEN = "my_secret_token"
            response = await ac.get("/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=my_secret_token&hub.challenge=123456")
            
            assert response.status_code == 200
            assert response.text == "123456"

@pytest.mark.asyncio
async def test_whatsapp_verify_webhook_invalid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        with patch("app.api.whatsapp.settings") as mock_settings:
            mock_settings.WHATSAPP_VERIFY_TOKEN = "my_secret_token"
            response = await ac.get("/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=wrong_token&hub.challenge=123456")
            
            assert response.status_code == 403

@pytest.mark.asyncio
async def test_whatsapp_webhook_valid(mock_adapter, mock_processor):
    payload = {"entry": []} # Payload content doesn't matter because we mock receive_message
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/webhooks/whatsapp", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
    mock_adapter.receive_message.assert_called_once_with(payload)
    mock_processor.assert_called_once()

@pytest.mark.asyncio
async def test_whatsapp_webhook_duplicate(mock_adapter):
    mock_adapter.receive_message = AsyncMock(return_value=None)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/webhooks/whatsapp", json={})
        
    assert response.status_code == 200
    assert response.json() == {"status": "ignored or duplicate"}
