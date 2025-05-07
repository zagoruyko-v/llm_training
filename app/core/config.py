import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LLM Experimentation Platform"

    # Ollama Settings
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "localhost")
    OLLAMA_PORT: int = int(os.getenv("OLLAMA_PORT", "11434"))

    # Model Settings
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "mistral:7b-instruct-q4")
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2000

    # Memory Management
    MODEL_MEMORY_REQUIREMENT: float = 4.0  # GB

    # Django Admin API Settings
    DJANGO_ADMIN_HOST: str = os.getenv("DJANGO_ADMIN_HOST", "admin")
    DJANGO_ADMIN_PORT: int = int(os.getenv("DJANGO_ADMIN_PORT", "8001"))

    class Config:
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
