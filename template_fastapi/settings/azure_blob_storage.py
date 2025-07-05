from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    azure_blob_storage_connection_string: str = (
        "DefaultEndpointsProtocol=https;AccountName=<YOUR_STORAGE_ACCOUNT>;AccountKey=<YOUR_ACCOUNT_KEY>;EndpointSuffix=core.windows.net"
    )
    azure_blob_storage_container_name: str = "<YOUR_CONTAINER_NAME>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_azure_blob_storage_settings() -> Settings:
    return Settings()