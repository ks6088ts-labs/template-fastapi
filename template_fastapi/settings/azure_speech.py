from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    azure_speech_key: str = "<YOUR_SPEECH_KEY>"
    azure_speech_region: str = "<YOUR_SPEECH_REGION>"
    azure_speech_endpoint: str = "https://<YOUR_SPEECH_REGION>.api.cognitive.microsoft.com/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_azure_speech_settings() -> Settings:
    return Settings()