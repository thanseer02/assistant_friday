from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone
from app.database.session import Base

class ProcessedWhatsAppMessage(Base):
    __tablename__ = "processed_whatsapp_messages"

    wamid = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
