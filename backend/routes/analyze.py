import os
import zipfile
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from loguru import logger
from backend.services.log_parser import LogParser
from backend.ai_service import ai_service
from backend.utils.config import settings

router = APIRouter(prefix="/analyze", tags=["Analyze"])

def _extract_supported_files_from_zip(zip_path: str, temp_dir: str) -> dict:
    supported_extensions = {".log", ".txt", ".yaml", ".yml", ".json", ".tf"}
    extracted = {}

    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.namelist():
            if member.endswith("/") or os.path.basename(member).startswith("."):
                continue

            filename = os.path.basename(member)
            ext = os.path.splitext(filename)[1].lower()
            if filename.lower() == "dockerfile" or ext in supported_extensions:
                target_path = os.path.join(temp_dir, member)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                archive.extract(member, temp_dir)
                extracted[member] = target_path

    return extracted


def _build_project_content(file_paths: dict) -> str:
    output = []
    for archive_name, path in file_paths.items():
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
        except Exception:
            content = ""
        if not content:
            continue

        output.append(f"---\nFILE: {archive_name}\n---\n{content}\n")
    return "\n".join(output)

class AnalyzeTextRequest(BaseModel):
    content: str

class AnalyzeResponse(BaseModel):
    log_type: str
    cleaned_log: str
    analysis: str
@router.post("/project", response_model=AnalyzeResponse)
async def analyze_project(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".zip"):
            raise HTTPException(status_code=400, detail="Project upload must be a .zip archive")

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = os.path.join(temp_dir, file.filename)
            with open(archive_path, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):
                    buffer.write(chunk)

            supported_files = _extract_supported_files_from_zip(archive_path, temp_dir)
            if not supported_files:
                raise HTTPException(
                    status_code=400,
                    detail="No supported files were found in the archive. Include Dockerfile, YAML, Terraform, JSON, or log files."
                )

            project_content = _build_project_content(supported_files)
            if not project_content.strip():
                raise HTTPException(status_code=400, detail="Uploaded archive contained no readable supported files.")

            log_type = "project_archive"
            cleaned_log = LogParser.clean_log(project_content)
            analysis = ai_service.analyze_log(cleaned_log, log_type)

            return AnalyzeResponse(
                log_type=log_type,
                cleaned_log=cleaned_log,
                analysis=analysis
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in project upload analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
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
