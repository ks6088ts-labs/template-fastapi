from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ChatSettings(BaseSettings):
    """チャットサービスの設定"""
    # チャットルームの設定
    chat_default_room_id: str = "general"
    chat_default_room_name: str = "General Chat"
    chat_max_message_length: int = 1000
    chat_max_username_length: int = 50
    chat_max_room_name_length: int = 100
    
    # メッセージ履歴の設定
    chat_max_history_messages: int = 100
    chat_history_retention_hours: int = 24
    
    # WebSocketの設定
    chat_websocket_heartbeat_interval: int = 30
    chat_websocket_timeout: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_chat_settings() -> ChatSettings:
    return ChatSettings()