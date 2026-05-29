import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from loguru import logger
from backend.services.log_parser import LogParser
from backend.ai_service import ai_service
from backend.utils.config import settings

router = APIRouter(prefix="/analyze", tags=["Analyze"])

class AnalyzeTextRequest(BaseModel):
    content: str

class AnalyzeResponse(BaseModel):
    log_type: str
    cleaned_log: str
    analysis: str

@router.post("/text", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeTextRequest):
    try:
        content = request.content
        if not content.strip():
            raise HTTPException(status_code=400, detail="Log content cannot be empty")
            
        log_type = LogParser.detect_log_type(content)
        cleaned_log = LogParser.clean_log(content)
        
        analysis = ai_service.analyze_log(cleaned_log, log_type)
        
        return AnalyzeResponse(
            log_type=log_type,
            cleaned_log=cleaned_log,
            analysis=analysis
        )
    except Exception as e:
        logger.error(f"Error in text analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file", response_model=AnalyzeResponse)
async def analyze_file(file: UploadFile = File(...)):
    try:
        # Save file to uploads folder
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            # Stream upload in chunks to support larger files
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
                
        # Read saved file content
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        if not content.strip():
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
            
        log_type = LogParser.detect_log_type(content)
        cleaned_log = LogParser.clean_log(content)
        
        analysis = ai_service.analyze_log(cleaned_log, log_type)
        
        return AnalyzeResponse(
            log_type=log_type,
            cleaned_log=cleaned_log,
            analysis=analysis
        )
    except Exception as e:
        logger.error(f"Error in file upload/analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
