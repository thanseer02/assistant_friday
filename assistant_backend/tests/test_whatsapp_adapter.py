import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
from app.integrations.whatsapp.adapter import WhatsAppAdapter
from app.schemas.integration import OutgoingMessage

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def adapter(mock_db):
    return WhatsAppAdapter(mock_db)

@pytest.mark.asyncio
async def test_receive_message_valid(adapter, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "id": "wamid_123",
                        "type": "text",
                        "from": "15551234567",
                        "text": {"body": "Hello bot"},
                        "timestamp": "1690000000"
                    }]
                }
            }]
        }]
    }
    
    msg = await adapter.receive_message(payload)
    assert msg is not None
    assert msg.platform == "whatsapp"
    assert msg.platform_user_id == "15551234567"
    assert msg.conversation_id == "wa_chat_15551234567"
    assert msg.text == "Hello bot"
    assert isinstance(msg.timestamp, datetime)
    assert msg.metadata["whatsapp_wamid"] == "wamid_123"
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_receive_message_duplicate(adapter, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
    
    payload = {
        "entry": [{"changes": [{"value": {"messages": [{"id": "wamid_123"}]}}]}]
    }
    msg = await adapter.receive_message(payload)
    assert msg is None
    mock_db.add.assert_not_called()

@pytest.mark.asyncio
async def test_receive_message_non_text(adapter, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    payload = {
        "entry": [{"changes": [{"value": {"messages": [{"id": "wamid_123", "type": "image"}]}}]}]
    }
    msg = await adapter.receive_message(payload)
    assert msg is None

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_send_message(mock_post, adapter):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    outgoing = OutgoingMessage(
        platform="whatsapp",
        platform_user_id="15551234567",
        conversation_id="wa_chat_15551234567",
        text="Test reply"
    )
    
    success = await adapter.send_message(outgoing)
    assert success is True
    
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["to"] == "15551234567"
    assert kwargs["json"]["text"]["body"] == "Test reply"
