from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    REDIS_PORT: str
    REDIS_HOST: str = 'redis'
    REDIS_URL: Optional[str] = None
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini-2024-07-18"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.3
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def redis_connection_url(self) -> str:
        if self.REDIS_URL is not None:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings():
    return Settings()
