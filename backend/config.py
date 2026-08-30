from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    LLM_PROVIDER: str = "google"
    LLM_MODEL: str = "gemini-2.0-flash"
    LLM_API_KEY: str = ""
    
    DATABASE_URL: str = "sqlite:///./neuronpath.db"
    
    JWT_SECRET_KEY: str = "neuronpath-super-secret-jwt-key-2026-production-ready"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173", 
        "http://127.0.0.1:5173", 
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
