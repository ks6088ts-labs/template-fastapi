from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    azure_ai_foundry_project_endpoint: str = "https://xxx.services.ai.azure.com/api/projects/yyy"
    azure_ai_foundry_api_key: str = "<YOUR_API_KEY>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_azure_ai_foundry_settings() -> Settings:
    return Settings()
