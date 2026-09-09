from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.config import settings
from app.core.logging import logger
from app.integrations.whatsapp.adapter import WhatsAppAdapter
from app.services.ai_service import AIService
from app.services.memory_service import MemoryService
from app.api.chat import background_extract_memories
from app.core.message_processor import process_incoming_message

router = APIRouter()

def get_ai_service():
    return AIService()

def get_memory_service(db: Session = Depends(get_db)):
    return MemoryService(db)

async def background_send_message(adapter: WhatsAppAdapter, outgoing_msg):
    await adapter.send_message(outgoing_msg)

@router.get("/webhooks/whatsapp", response_class=PlainTextResponse)
async def whatsapp_verify_webhook(request: Request):
    """
    Meta webhook verification challenge.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully.")
        return challenge
    
    logger.warning("WhatsApp webhook verification failed.")
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    Receives incoming WhatsApp messages.
    """
    payload = await request.json()
    adapter = WhatsAppAdapter(db)
    
    incoming_msg = await adapter.receive_message(payload)
    if not incoming_msg:
        # Either duplicate, non-text, status update, or unprocessable
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
