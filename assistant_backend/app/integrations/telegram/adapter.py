import httpx
from typing import Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.schemas.integration import IncomingMessage
from app.models.telegram import ProcessedTelegramUpdate

class TelegramAdapter:
    def __init__(self, db: Session):
        self.db = db
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def parse_update(self, payload: dict[str, Any]) -> IncomingMessage | None:
        """
        Parses a Telegram webhook payload into an internal IncomingMessage format.
        Checks for duplicate update_ids to prevent double processing.
        Returns None if it's a duplicate or missing message text.
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

        if not text or not chat_id:
            return None

        # Map Telegram chat_id directly to conversation_id
        conversation_id = f"tg_chat_{chat_id}"

        return IncomingMessage(
            platform="telegram",
            platform_user_id=user_id,
            conversation_id=conversation_id,
            text=text,
            metadata={"telegram_update_id": update_id, "telegram_chat_id": chat_id}
        )

    async def send_message(self, chat_id: str, text: str) -> bool:
        """
        Sends a text message back to the Telegram chat.
        """
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
            return False
