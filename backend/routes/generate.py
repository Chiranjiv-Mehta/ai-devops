from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from backend.ai_service import ai_service
from loguru import logger

router = APIRouter(prefix="/generate", tags=["Generate"])

class GenerateRequest(BaseModel):
    template_type: str  # e.g., "dockerfile", "kubernetes", "github_actions", "terraform"
    details: Dict[str, Any]

class GenerateResponse(BaseModel):
    template: str

@router.post("", response_model=GenerateResponse)
async def generate_config(request: GenerateRequest):
    try:
        if not request.template_type:
            raise HTTPException(status_code=400, detail="template_type is required")
            
        template = ai_service.generate_iac_template(request.template_type, request.details)
        return GenerateResponse(template=template)
    except Exception as e:
        logger.error(f"Error generating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))
