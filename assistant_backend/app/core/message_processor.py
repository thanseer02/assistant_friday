from sqlalchemy.orm import Session
from app.schemas.integration import IncomingMessage, OutgoingMessage
from app.services.conversation_service import ConversationService
from app.services.memory_service import MemoryService
from app.services.ai_service import AIService
from app.services.action_service import ActionPermissionService
from app.core.exceptions import PendingActionException
from app.api.chat import tool_registry

async def process_incoming_message(
    incoming_msg: IncomingMessage,
    db: Session,
    ai_service: AIService,
    memory_service: MemoryService
) -> OutgoingMessage:
    """
    Core function to process messages from ANY platform.
    It manages conversation state, retrieves memories, coordinates with the AI engine,
    and formats the final output into a platform-agnostic OutgoingMessage.
    """
    conversation_service = ConversationService(db)
    
    # 1. Ensure conversation exists and add user message
    conversation = conversation_service.get_or_create_conversation(incoming_msg.conversation_id)
    conversation_service.add_message(conversation.id, "user", incoming_msg.text)
    
    # 2. Retrieve history and memories
    history = conversation_service.get_conversation_history(conversation.id)
    memories_db = memory_service.search_memories(incoming_msg.text)
    memory_strings = [f"{m.key}: {m.value}" for m in memories_db]
    
    # 3. Generate Response
    try:
        response_text = await ai_service.generate_response(
            history, 
            memories=memory_strings, 
            tool_registry=tool_registry
        )
    except PendingActionException as e:
        # Handle sensitive tools gracefully
        action_service = ActionPermissionService(db)
        pending = action_service.create_pending_action(
            conversation_id=conversation.id,
            tool_name=e.tool_name,
            arguments=e.arguments
        )
        response_text = f"Action '{e.tool_name}' requires your confirmation. (Action ID: {pending.id})"
        
    # 4. Save AI Response
    conversation_service.add_message(conversation.id, "assistant", response_text)
    
    # 5. Return OutgoingMessage
    return OutgoingMessage(
        platform=incoming_msg.platform,
        platform_user_id=incoming_msg.platform_user_id,
        conversation_id=incoming_msg.conversation_id,
        text=response_text,
        metadata=incoming_msg.metadata
    )
