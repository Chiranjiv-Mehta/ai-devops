import sys
import os

# Prevent protobuf from trying to import broken C extension on Python 3.14
sys.modules['google._upb._message'] = None

# Adjust path to import backend modules when running from within the backend directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from backend.utils.config import settings
from backend.routes import chat, analyze, generate


# Configure Loguru logging
logger.remove()
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    "../logs/backend.log",
    rotation="10 MB",
    retention="10 days",
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# Initialize FastAPI App
app = FastAPI(
    title="AI DevOps Assistant API",
    description="Backend API for the intelligent AI DevOps Assistant dashboard",
    version="1.0.0"
)

# CORS Configuration
origins = [org.strip() for org in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(generate.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up AI DevOps Assistant Backend...")
    # Validate LLM configs
    settings.validate_keys()
    # Log configuration summary
    logger.info(f"API listening on {settings.API_HOST}:{settings.API_PORT}")
    
@app.get("/health", tags=["Health"])
async def health_check():
    """Simple API health check endpoint"""
    return {
        "status": "healthy",
        "default_provider": settings.DEFAULT_PROVIDER,
        "gemini_active": settings.GEMINI_API_KEY != "",
        "openai_active": settings.OPENAI_API_KEY != ""
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
