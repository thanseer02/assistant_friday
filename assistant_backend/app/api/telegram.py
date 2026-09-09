from fastapi import APIRouter, Depends, Request, HTTPException, Header, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.config import settings
from app.core.logging import logger
from app.integrations.telegram.adapter import TelegramAdapter
from app.services.conversation_service import ConversationService
from app.services.ai_service import AIService
from app.services.memory_service import MemoryService
from app.api.chat import tool_registry, background_extract_memories
from app.core.exceptions import PendingActionException
from app.services.action_service import ActionPermissionService

router = APIRouter()

def get_conversation_service(db: Session = Depends(get_db)):
    return ConversationService(db)

def get_ai_service():
    return AIService()

def get_memory_service(db: Session = Depends(get_db)):
    return MemoryService(db)

@router.post("/webhooks/telegram")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str = Header(None),
    db: Session = Depends(get_db),
    conversation_service: ConversationService = Depends(get_conversation_service),
    ai_service: AIService = Depends(get_ai_service),
    memory_service: MemoryService = Depends(get_memory_service)
):
    # Security check: verify the secret token if configured
    if settings.TELEGRAM_WEBHOOK_SECRET:
        if x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
            logger.warning("Unauthorized Telegram webhook access attempt.")
            raise HTTPException(status_code=401, detail="Unauthorized")

    payload = await request.json()
    adapter = TelegramAdapter(db)
    
    incoming_msg = adapter.parse_update(payload)
    if not incoming_msg:
        # Either duplicate or unprocessable (e.g., system message)
        return {"status": "ignored or duplicate"}

    # Process the message via the Assistant Core (similar to /api/chat)
    conversation = conversation_service.get_or_create_conversation(incoming_msg.conversation_id)
    conversation_service.add_message(conversation.id, "user", incoming_msg.text)
    
    history = conversation_service.get_conversation_history(conversation.id)
    memories_db = memory_service.search_memories(incoming_msg.text)
    memory_strings = [f"{m.key}: {m.value}" for m in memories_db]

    tg_chat_id = incoming_msg.metadata.get("telegram_chat_id")

    try:
        response_text = await ai_service.generate_response(
            history, 
            memories=memory_strings, 
            tool_registry=tool_registry
        )
    except PendingActionException as e:
        # Handle sensitive tools gracefully over Telegram
        action_service = ActionPermissionService(db)
        pending = action_service.create_pending_action(
            conversation_id=conversation.id,
            tool_name=e.tool_name,
            arguments=e.arguments
        )
        response_text = f"Action '{e.tool_name}' requires your confirmation. (Action ID: {pending.id})"
        # (In the future, inline keyboard buttons could be sent here to approve/reject)

    conversation_service.add_message(conversation.id, "assistant", response_text)
    background_tasks.add_task(background_extract_memories, incoming_msg.text, ai_service, memory_service)

    # Send the response back to Telegram asynchronously
    background_tasks.add_task(adapter.send_message, tg_chat_id, response_text)

    return {"status": "ok"}
