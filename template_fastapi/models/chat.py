from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """チャットメッセージモデル"""
    id: str
    user_id: str
    username: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    room_id: str = "general"


class ChatUser(BaseModel):
    """チャットユーザーモデル"""
    user_id: str
    username: str
    room_id: str = "general"
    connected_at: datetime = Field(default_factory=datetime.now)


class ChatRoom(BaseModel):
    """チャットルームモデル"""
    room_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    user_count: int = 0


class ChatMessageRequest(BaseModel):
    """チャットメッセージ送信リクエスト"""
    message: str
    room_id: str = "general"


class ChatJoinRequest(BaseModel):
    """チャットルーム参加リクエスト"""
    username: str
    room_id: str = "general"


class ChatHistory(BaseModel):
    """チャット履歴レスポンス"""
    room_id: str
    messages: list[ChatMessage]
    total_messages: int