from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    SECRET_KEY: str = Field(..., min_length=16)
    APP_NAME: str = "SecRAG AI"
    APP_VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = Field(...)

    # Storage paths
    UPLOAD_DIR: str = "./uploads"
    MODELS_DIR: str = "./stored_models"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_TIMEOUT: int = 120

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    def ensure_directories(self):
        """Create required storage directories if they don't exist."""
        for d in [self.UPLOAD_DIR, self.MODELS_DIR, self.CHROMA_PERSIST_DIR]:
            Path(d).mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
