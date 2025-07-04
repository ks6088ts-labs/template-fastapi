from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    azure_cosmosdb_connection_string: str = (
        "AccountEndpoint=https://<YOUR_COSMOSDB_NAME>.documents.azure.com:443/;AccountKey=<ACCOUNT_KEY>;"
    )
    azure_cosmosdb_database_name: str = "<YOUR_DATABASE_NAME>"
    azure_cosmosdb_container_name: str = "<YOUR_CONTAINER_NAME>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_azure_cosmosdb_settings() -> Settings:
    return Settings()
