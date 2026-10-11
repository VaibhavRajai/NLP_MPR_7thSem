from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Healthcare Research Paper Summarizer"
    API_V1_STR: str = "/api"
    MAX_FILE_SIZE_MB: int = 30
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]
    DEFAULT_MAX_SUMMARY_SENTENCES: int = 8
    
    # Storage directories
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "uploads")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
