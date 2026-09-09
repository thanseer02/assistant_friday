from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime, timezone
from app.database.session import Base

class ProcessedTelegramUpdate(Base):
    __tablename__ = "processed_telegram_updates"

    update_id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
