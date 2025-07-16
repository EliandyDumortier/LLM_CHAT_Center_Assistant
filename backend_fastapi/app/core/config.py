from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Ollama Configuration
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    
    # Chroma Configuration
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "airbnb_support"
    
    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:3000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()