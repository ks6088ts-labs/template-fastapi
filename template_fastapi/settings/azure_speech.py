from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    azure_ai_speech_api_key: str = "<YOUR_AZURE_AI_SPEECH_API_KEY>"
    azure_ai_speech_endpoint: str = "https://<speech-api-name>.cognitiveservices.azure.com/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_azure_speech_settings() -> Settings:
    return Settings()
