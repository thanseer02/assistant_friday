from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIService
from app.services.conversation_service import ConversationService
from app.database.session import get_db

router = APIRouter()

def get_ai_service():
    return AIService()

def get_conversation_service(db: Session = Depends(get_db)):
    return ConversationService(db)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    ai_service: AIService = Depends(get_ai_service),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    # 1. Get or create conversation
    conversation = conversation_service.get_or_create_conversation(request.conversation_id)
    
    # 2. Save the user message
    conversation_service.add_message(conversation.id, "user", request.message)
    
    # 3. Retrieve conversation history
    history = conversation_service.get_conversation_history(conversation.id)
    
    # 4. Generate response via AI
    response_text = await ai_service.generate_response(history)
    
    # 5. Save AI response
    conversation_service.add_message(conversation.id, "assistant", response_text)
    
    # 6. Return response with conversation_id
    return ChatResponse(conversation_id=conversation.id, response=response_text)
