from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.ai_service import ai_service

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatTurn(BaseModel):
    role: str  # 'user' or 'assistant' / 'model'
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatTurn]] = []

class ChatResponse(BaseModel):
    response: str

@router.post("", response_model=ChatResponse)
async def devops_chat(request: ChatRequest):
    try:
        history_list = []
        if request.history:
            history_list = [{"role": turn.role, "content": turn.content} for turn in request.history]
        
        response_text = ai_service.run_devops_chat(request.message, history_list)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")
