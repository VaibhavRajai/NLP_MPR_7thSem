from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Healthcare Research Paper Summarizer"
    API_V1_STR: str = "/api"
    MAX_FILE_SIZE_MB: int = 30
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]
    DEFAULT_MAX_SUMMARY_SENTENCES: int = 8

    # T5 abstractive summarization (fine-tuned PubMed model)
    T5_ENABLED: bool = True
    T5_MODEL_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "t5-pubmed-finetuned",
    )
    T5_MAX_INPUT_TOKENS: int = 480
    T5_MAX_NEW_TOKENS: int = 200
    T5_MIN_NEW_TOKENS: int = 30
    T5_NUM_BEAMS: int = 4
    # If True, the query is also prepended to the T5 input text ("summarize: <query>. <evidence>").
    # Default False: the query conditions generation through evidence retrieval instead.
    T5_PREPEND_QUERY: bool = False
    
    # Storage directories
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "uploads")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
