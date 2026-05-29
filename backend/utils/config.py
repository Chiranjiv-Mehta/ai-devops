import os
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from loguru import logger

# Load environment variables from .env
load_dotenv()

class Settings:
    def __init__(self):
        self.API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT: int = int(os.getenv("API_PORT", "8000"))
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
        self.UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "../uploads")
        
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        
        self.DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "gemini").lower()
        self.GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro-latest")
        self.OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        
        # Ensure upload directory exists
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        
    def validate_keys(self):
        """Log key statuses (obscured for security)"""
        logger.info(f"Using default LLM Provider: {self.DEFAULT_PROVIDER}")
        if self.DEFAULT_PROVIDER == "gemini":
            if self.GEMINI_API_KEY:
                logger.info("Gemini API Key: LOADED")
            else:
                logger.warning("Gemini API Key: NOT LOADED. AI requests may fail if Gemini is called.")
        elif self.DEFAULT_PROVIDER == "openai":
            if self.OPENAI_API_KEY:
                logger.info("OpenAI API Key: LOADED")
            else:
                logger.warning("OpenAI API Key: NOT LOADED. AI requests may fail if OpenAI is called.")

settings = Settings()
