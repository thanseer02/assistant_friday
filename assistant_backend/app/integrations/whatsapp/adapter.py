import httpx
from typing import Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.integrations.base import MessagingPlatform
from app.schemas.integration import IncomingMessage, OutgoingMessage
from app.models.whatsapp import ProcessedWhatsAppMessage
from datetime import datetime, timezone

class WhatsAppAdapter(MessagingPlatform):
    def __init__(self, db: Session):
        self.db = db
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.api_url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}/messages"

    async def receive_message(self, payload: dict[str, Any]) -> IncomingMessage | None:
        """
        Parses a WhatsApp webhook payload into an internal IncomingMessage format.
        Checks for duplicate wamid to prevent double processing.
        Only processes text messages for now.
        """
        try:
            entry = payload.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            
            if not messages:
                # E.g., status updates (delivered/read)
                return None
                
            message = messages[0]
            wamid = message.get("id")
            
            if not wamid:
                return None

            # Check for duplicate
            existing = self.db.query(ProcessedWhatsAppMessage).filter(ProcessedWhatsAppMessage.wamid == wamid).first()
            if existing:
                logger.warning(f"Dropping duplicate WhatsApp message id: {wamid}")
                return None

            # Record update to prevent duplicates
            new_msg = ProcessedWhatsAppMessage(wamid=wamid)
            self.db.add(new_msg)
            self.db.commit()

            msg_type = message.get("type")
            if msg_type != "text":
                logger.info(f"Ignoring non-text WhatsApp message type: {msg_type}")
                return None
                
            text = message.get("text", {}).get("body")
            sender_id = message.get("from")
            timestamp_str = message.get("timestamp")
            
            if not text or not sender_id:
                return None

            conversation_id = f"wa_chat_{sender_id}"
            
            # Convert WhatsApp's unix timestamp string to datetime
            timestamp = datetime.fromtimestamp(int(timestamp_str), tz=timezone.utc) if timestamp_str else datetime.now(timezone.utc)

            return IncomingMessage(
                platform="whatsapp",
                platform_user_id=sender_id,
                conversation_id=conversation_id,
                text=text,
                timestamp=timestamp,
                metadata={"whatsapp_wamid": wamid}
            )
        except (IndexError, KeyError, TypeError) as e:
            logger.error(f"Error parsing WhatsApp payload: {e}")
            return None

    async def send_message(self, message: OutgoingMessage) -> bool:
        """
        Sends an OutgoingMessage back to the WhatsApp chat using the Graph API.
        """
        phone_number = message.platform_user_id
            
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message.text}
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, json=payload, headers=headers)
                
                if response.status_code == 429:
                    logger.error(f"WhatsApp API rate limit exceeded.")
                    return False
                
                if response.status_code >= 400:
                    logger.error(f"WhatsApp API error {response.status_code}: {response.text}")
                    # Could be outside 24h window
                    return False
                    
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message to {phone_number}: {e}")
            return False

    async def get_user(self, platform_user_id: str) -> dict[str, Any]:
        """Stub for getting user profile from WhatsApp."""
        return {"id": platform_user_id, "platform": "whatsapp"}

    async def health_check(self) -> bool:
        """Stub for checking WhatsApp API health."""
        return True
