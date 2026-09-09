from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.services.conversation_service import ConversationService
from app.schemas.conversation import ConversationSchema, ConversationListSchema

router = APIRouter()

def get_conversation_service(db: Session = Depends(get_db)):
    return ConversationService(db)

@router.get("/conversations", response_model=List[ConversationListSchema])
def get_conversations(
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get all conversations."""
    return conversation_service.get_all_conversations()

@router.get("/conversations/{conversation_id}", response_model=ConversationSchema)
def get_conversation(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get a specific conversation by ID."""
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return conversation

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Delete a conversation by ID."""
    success = conversation_service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
