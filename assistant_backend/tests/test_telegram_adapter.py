import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
from app.integrations.telegram.adapter import TelegramAdapter
from app.schemas.integration import OutgoingMessage

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def adapter(mock_db):
    return TelegramAdapter(mock_db)

@pytest.mark.asyncio
async def test_receive_message_valid(adapter, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    payload = {
        "update_id": 12345,
        "message": {
            "chat": {"id": 9876},
            "from": {"id": 1111},
            "text": "Hello bot",
            "date": 1690000000
        }
    }
    
    msg = await adapter.receive_message(payload)
    assert msg is not None
    assert msg.platform == "telegram"
    assert msg.platform_user_id == "1111"
    assert msg.conversation_id == "tg_chat_9876"
    assert msg.text == "Hello bot"
    assert isinstance(msg.timestamp, datetime)
    assert msg.metadata["telegram_update_id"] == 12345
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_receive_message_duplicate(adapter, mock_db):
    # Mock existing update
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
    
    payload = {"update_id": 12345, "message": {"text": "hello"}}
    msg = await adapter.receive_message(payload)
    assert msg is None
    mock_db.add.assert_not_called()

@pytest.mark.asyncio
async def test_receive_message_invalid(adapter, mock_db):
    payload = {"update_id": 12345} # Missing message
    msg = await adapter.receive_message(payload)
    assert msg is None

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_send_message(mock_post, adapter):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    outgoing = OutgoingMessage(
        platform="telegram",
        platform_user_id="1111",
        conversation_id="tg_chat_9876",
        text="Test reply",
        metadata={"telegram_chat_id": "9876"}
    )
    
    success = await adapter.send_message(outgoing)
    assert success is True
    
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["chat_id"] == "9876"
    assert kwargs["json"]["text"] == "Test reply"
