from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIService

router = APIRouter()

def get_ai_service():
    return AIService()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, ai_service: AIService = Depends(get_ai_service)):
    response_text = await ai_service.generate_response(request.message)
    return ChatResponse(response=response_text)
