import pytest
from unittest.mock import MagicMock
from app.services.conversation_service import ConversationService
from app.models.conversation import Conversation, Message, RoleEnum

@pytest.fixture
def db_session_mock():
    return MagicMock()

@pytest.fixture
def conversation_service(db_session_mock):
    return ConversationService(db_session_mock)

def test_get_or_create_conversation_existing(conversation_service, db_session_mock):
    mock_conv = Conversation(id="existing-id")
    db_session_mock.query.return_value.filter.return_value.first.return_value = mock_conv
    
    conv = conversation_service.get_or_create_conversation("existing-id")
    assert conv.id == "existing-id"
    db_session_mock.add.assert_not_called()

def test_get_or_create_conversation_new(conversation_service, db_session_mock):
    db_session_mock.query.return_value.filter.return_value.first.return_value = None
    
    conv = conversation_service.get_or_create_conversation(None)
    assert conv.title == "New Chat"
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()
    db_session_mock.refresh.assert_called_once()

def test_add_message(conversation_service, db_session_mock):
    msg = conversation_service.add_message("conv-id", "user", "Hello")
    assert msg.conversation_id == "conv-id"
    assert msg.role == RoleEnum.user
    assert msg.content == "Hello"
    
    db_session_mock.add.assert_called_once()
    db_session_mock.commit.assert_called_once()

def test_get_conversation_history(conversation_service, db_session_mock):
    msg1 = Message(role=RoleEnum.user, content="Hi")
    msg2 = Message(role=RoleEnum.assistant, content="Hello there!")
    
    db_session_mock.query.return_value.filter.return_value.order_by.return_value.all.return_value = [msg1, msg2]
    
    history = conversation_service.get_conversation_history("conv-id")
    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "Hi"}
    assert history[1] == {"role": "assistant", "content": "Hello there!"}
