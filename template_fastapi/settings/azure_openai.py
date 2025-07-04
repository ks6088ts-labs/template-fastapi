from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    azure_openai_endpoint: str = "https://<YOUR_AOAI_NAME>.openai.azure.com/"
    azure_openai_api_key: str = "<YOUR_API_KEY>"
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_model_chat: str = "gpt-4o"
    azure_openai_model_embedding: str = "text-embedding-3-small"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_azure_openai_settings() -> Settings:
    return Settings()
