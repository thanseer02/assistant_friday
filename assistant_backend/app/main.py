from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import add_exception_handlers
from app.api import health, chat, memories, actions, telegram, whatsapp

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Exception handlers
add_exception_handlers(app)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(memories.router, prefix="/api", tags=["Memories"])
app.include_router(actions.router, prefix="/api", tags=["Actions"])
app.include_router(telegram.router, tags=["Webhooks"])
app.include_router(whatsapp.router, tags=["Webhooks"])

from app.database.session import engine
from app.models.conversation import Base
from app.models.memory import Memory
from app.models.action import PendingAction
from app.models.telegram import ProcessedTelegramUpdate
from app.models.whatsapp import ProcessedWhatsAppMessage

# Create tables
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME}...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
