import httpx
from typing import Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.integrations.base import MessagingPlatform
from app.schemas.integration import IncomingMessage, OutgoingMessage
from app.models.telegram import ProcessedTelegramUpdate
from datetime import datetime, timezone

class TelegramAdapter(MessagingPlatform):
    def __init__(self, db: Session):
        self.db = db
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def receive_message(self, payload: dict[str, Any]) -> IncomingMessage | None:
        """
        Parses a Telegram webhook payload into an internal IncomingMessage format.
        Checks for duplicate update_ids to prevent double processing.
        """
        update_id = payload.get("update_id")
        if not update_id:
            return None

        # Check for duplicate
        existing = self.db.query(ProcessedTelegramUpdate).filter(ProcessedTelegramUpdate.update_id == update_id).first()
        if existing:
            logger.warning(f"Dropping duplicate Telegram update_id: {update_id}")
            return None

        # Record update to prevent duplicates
        new_update = ProcessedTelegramUpdate(update_id=update_id)
        self.db.add(new_update)
        self.db.commit()

        message = payload.get("message")
        if not message:
            return None

        chat_id = str(message.get("chat", {}).get("id"))
        user_id = str(message.get("from", {}).get("id"))
        text = message.get("text")
        date = message.get("date")

        if not text or not chat_id:
            return None

        conversation_id = f"tg_chat_{chat_id}"
        
        # Convert Telegram's unix timestamp to datetime
        timestamp = datetime.fromtimestamp(date, tz=timezone.utc) if date else datetime.now(timezone.utc)

        return IncomingMessage(
            platform="telegram",
            platform_user_id=user_id,
            conversation_id=conversation_id,
            text=text,
            timestamp=timestamp,
            metadata={"telegram_update_id": update_id, "telegram_chat_id": chat_id}
        )

    async def send_message(self, message: OutgoingMessage) -> bool:
        """
        Sends an OutgoingMessage back to the Telegram chat.
        """
        chat_id = message.metadata.get("telegram_chat_id") if message.metadata else None
        if not chat_id:
            # Fallback if metadata is missing
            chat_id = message.conversation_id.replace("tg_chat_", "")
            
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message.text
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
            return False

    async def get_user(self, platform_user_id: str) -> dict[str, Any]:
        """Stub for getting user profile from Telegram."""
        return {"id": platform_user_id, "platform": "telegram"}

    async def health_check(self) -> bool:
        """Stub for checking Telegram API health."""
        return True
