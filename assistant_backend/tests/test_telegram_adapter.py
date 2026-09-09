import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.integrations.telegram.adapter import TelegramAdapter

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def adapter(mock_db):
    return TelegramAdapter(mock_db)

def test_parse_update_valid(adapter, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    payload = {
        "update_id": 12345,
        "message": {
            "chat": {"id": 9876},
            "from": {"id": 1111},
            "text": "Hello bot"
        }
    }
    
    msg = adapter.parse_update(payload)
    assert msg is not None
    assert msg.platform == "telegram"
    assert msg.platform_user_id == "1111"
    assert msg.conversation_id == "tg_chat_9876"
    assert msg.text == "Hello bot"
    assert msg.metadata["telegram_update_id"] == 12345
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_parse_update_duplicate(adapter, mock_db):
    # Mock existing update
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
    
    payload = {"update_id": 12345, "message": {"text": "hello"}}
    msg = adapter.parse_update(payload)
    assert msg is None
    mock_db.add.assert_not_called()

def test_parse_update_invalid(adapter, mock_db):
    payload = {"update_id": 12345} # Missing message
    msg = adapter.parse_update(payload)
    assert msg is None

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_send_message(mock_post, adapter):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    success = await adapter.send_message("9876", "Test reply")
    assert success is True
    
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["json"]["chat_id"] == "9876"
    assert kwargs["json"]["text"] == "Test reply"
