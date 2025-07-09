from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    azure_ai_foundry_project_connection_string: str = "https://<YOUR_PROJECT_NAME>.eastus.inference.ai.azure.com"
    azure_ai_foundry_api_key: str = "<YOUR_API_KEY>"
    azure_ai_foundry_project_id: str = "<YOUR_PROJECT_ID>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_azure_ai_foundry_settings() -> Settings:
    return Settings()
