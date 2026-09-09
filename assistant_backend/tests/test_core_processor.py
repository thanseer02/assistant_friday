import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone
from app.schemas.integration import IncomingMessage, OutgoingMessage
from app.core.message_processor import process_incoming_message
from app.core.exceptions import PendingActionException

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_ai_service():
    mock = MagicMock()
    mock.generate_response = AsyncMock(return_value="Generic AI Reply")
    return mock

@pytest.fixture
def mock_memory_service():
    mock = MagicMock()
    mock.search_memories.return_value = []
    return mock

@pytest.mark.asyncio
async def test_process_incoming_message_success(mock_db, mock_ai_service, mock_memory_service):
    incoming = IncomingMessage(
        platform="discord",
        platform_user_id="user1",
        conversation_id="conv_1",
        text="Hello AI",
        timestamp=datetime.now(timezone.utc),
        metadata={"custom": "data"}
    )

    with patch("app.core.message_processor.ConversationService") as MockConvService:
        mock_conv_service = MockConvService.return_value
        mock_conv = MagicMock()
        mock_conv.id = "conv_1"
        mock_conv_service.get_or_create_conversation.return_value = mock_conv
        mock_conv_service.get_conversation_history.return_value = []

        outgoing = await process_incoming_message(incoming, mock_db, mock_ai_service, mock_memory_service)

        assert isinstance(outgoing, OutgoingMessage)
        assert outgoing.platform == "discord"
        assert outgoing.conversation_id == "conv_1"
        assert outgoing.text == "Generic AI Reply"
        assert outgoing.metadata == {"custom": "data"}
        
        mock_conv_service.add_message.assert_any_call("conv_1", "user", "Hello AI")
        mock_conv_service.add_message.assert_any_call("conv_1", "assistant", "Generic AI Reply")

@pytest.mark.asyncio
async def test_process_incoming_message_pending_action(mock_db, mock_ai_service, mock_memory_service):
    incoming = IncomingMessage(
        platform="whatsapp",
        platform_user_id="user2",
        conversation_id="conv_2",
        text="Delete my file",
        timestamp=datetime.now(timezone.utc)
    )

    mock_ai_service.generate_response.side_effect = PendingActionException(tool_name="delete_file", arguments={"file": "test.txt"})

    with patch("app.core.message_processor.ConversationService") as MockConvService, \
         patch("app.core.message_processor.ActionPermissionService") as MockActionService:
        
        mock_conv_service = MockConvService.return_value
        mock_conv = MagicMock()
        mock_conv.id = "conv_2"
        mock_conv_service.get_or_create_conversation.return_value = mock_conv
        
        mock_action_service = MockActionService.return_value
        mock_pending = MagicMock()
        mock_pending.id = "action_123"
        mock_action_service.create_pending_action.return_value = mock_pending

        outgoing = await process_incoming_message(incoming, mock_db, mock_ai_service, mock_memory_service)

        assert "Action 'delete_file' requires your confirmation" in outgoing.text
        assert "action_123" in outgoing.text
