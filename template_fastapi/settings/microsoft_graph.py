from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    microsoft_graph_tenant_id: str = "<YOUR_TENANT_ID>"
    microsoft_graph_client_id: str = "<YOUR_CLIENT_ID>"
    microsoft_graph_client_secret: str = "<YOUR_CLIENT_SECRET>"
    microsoft_graph_site_id: str = "<YOUR_SITE_ID>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_microsoft_graph_settings() -> Settings:
    return Settings()