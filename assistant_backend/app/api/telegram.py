from fastapi import APIRouter, Depends, Request, HTTPException, Header, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.config import settings
from app.core.logging import logger
from app.integrations.telegram.adapter import TelegramAdapter
from app.services.ai_service import AIService
from app.services.memory_service import MemoryService
from app.api.chat import background_extract_memories
from app.core.message_processor import process_incoming_message

router = APIRouter()

def get_ai_service():
    return AIService()

def get_memory_service(db: Session = Depends(get_db)):
    return MemoryService(db)

async def background_send_message(adapter: TelegramAdapter, outgoing_msg):
    await adapter.send_message(outgoing_msg)

@router.post("/webhooks/telegram")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str = Header(None),
    db: Session = Depends(get_db),
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
    
    incoming_msg = await adapter.receive_message(payload)
    if not incoming_msg:
        # Either duplicate or unprocessable (e.g., system message)
        return {"status": "ignored or duplicate"}

    # Process the message via the Assistant Core
    outgoing_msg = await process_incoming_message(
        incoming_msg=incoming_msg,
        db=db,
        ai_service=ai_service,
        memory_service=memory_service
    )

    # Trigger background tasks
    background_tasks.add_task(background_extract_memories, incoming_msg.text, ai_service, memory_service)
    background_tasks.add_task(background_send_message, adapter, outgoing_msg)

    return {"status": "ok"}
