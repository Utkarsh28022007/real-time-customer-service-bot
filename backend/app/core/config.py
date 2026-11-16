import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Keys
    GEMINI_API_KEY: str = ""

    # Gemini Models (Using modern 2.5 series as specified)
    GEMINI_CHAT_MODEL: str = "gemini-2.5-flash"
    GEMINI_COMPLEX_MODEL: str = "gemini-2.5-pro"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

    # Application
    APP_NAME: str = "Real-Time Customer Service Bot"
    APP_ENV: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # Database & Vector Store
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/chatbot.db"
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    KNOWLEDGE_BASE_DIR: str = "./data/knowledge_base"

    # Memory & Guardrails
    MAX_HISTORY_TURNS: int = 10
    RATE_LIMIT_MESSAGES_PER_MINUTE: int = 20
    ESCALATION_SENTIMENT_THRESHOLD: float = -0.5

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip() and self.GEMINI_API_KEY != "your_gemini_api_key_here")


settings = Settings()
