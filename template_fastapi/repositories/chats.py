import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import WebSocket

from template_fastapi.models.chat import ChatMessage, ChatUser, ChatRoom, ChatHistory
from template_fastapi.settings.chats import get_chat_settings

# 設定を取得
chat_settings = get_chat_settings()


class ChatRepository:
    """チャットデータを管理するリポジトリクラス"""
    
    def __init__(self):
        # インメモリデータベース
        self.messages: Dict[str, List[ChatMessage]] = {}
        self.rooms: Dict[str, ChatRoom] = {}
        self.users: Dict[str, ChatUser] = {}
        self.connections: Dict[str, WebSocket] = {}
        
        # デフォルトルームを作成
        self._create_default_room()
    
    def _create_default_room(self):
        """デフォルトルームを作成"""
        default_room = ChatRoom(
            room_id=chat_settings.chat_default_room_id,
            name=chat_settings.chat_default_room_name,
            description="Default chat room for general conversations"
        )
        self.rooms[default_room.room_id] = default_room
        self.messages[default_room.room_id] = []
    
    def create_room(self, room_id: str, name: str, description: Optional[str] = None) -> ChatRoom:
        """新しいチャットルームを作成"""
        if room_id in self.rooms:
            raise ValueError(f"Room {room_id} already exists")
        
        room = ChatRoom(
            room_id=room_id,
            name=name,
            description=description
        )
        self.rooms[room_id] = room
        self.messages[room_id] = []
        return room
    
    def get_room(self, room_id: str) -> Optional[ChatRoom]:
        """ルーム情報を取得"""
        return self.rooms.get(room_id)
    
    def list_rooms(self) -> List[ChatRoom]:
        """全てのルームを一覧取得"""
        return list(self.rooms.values())
    
    def join_room(self, user_id: str, username: str, room_id: str, websocket: WebSocket) -> ChatUser:
        """ユーザーをルームに参加させる"""
        if room_id not in self.rooms:
            raise ValueError(f"Room {room_id} does not exist")
        
        # 既存のユーザーがあれば削除
        if user_id in self.users:
            old_room_id = self.users[user_id].room_id
            if old_room_id in self.rooms:
                self.rooms[old_room_id].user_count -= 1
        
        # ユーザー情報を作成/更新
        user = ChatUser(
            user_id=user_id,
            username=username,
            room_id=room_id
        )
        self.users[user_id] = user
        self.connections[user_id] = websocket
        
        # ルームのユーザー数を更新
        self.rooms[room_id].user_count += 1
        
        return user
    
    def leave_room(self, user_id: str):
        """ユーザーをルームから退出させる"""
        if user_id not in self.users:
            return
        
        user = self.users[user_id]
        room_id = user.room_id
        
        # ルームのユーザー数を減らす
        if room_id in self.rooms:
            self.rooms[room_id].user_count -= 1
        
        # ユーザー情報を削除
        del self.users[user_id]
        if user_id in self.connections:
            del self.connections[user_id]
    
    def add_message(self, user_id: str, message: str, room_id: str) -> ChatMessage:
        """メッセージを追加"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        if room_id not in self.rooms:
            raise ValueError(f"Room {room_id} not found")
        
        user = self.users[user_id]
        chat_message = ChatMessage(
            id=str(uuid.uuid4()),
            user_id=user_id,
            username=user.username,
            message=message,
            room_id=room_id
        )
        
        # メッセージを保存
        self.messages[room_id].append(chat_message)
        
        # 古いメッセージを削除（最大数を超えた場合）
        if len(self.messages[room_id]) > chat_settings.chat_max_history_messages:
            self.messages[room_id] = self.messages[room_id][-chat_settings.chat_max_history_messages:]
        
        return chat_message
    
    def get_messages(self, room_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """ルームのメッセージを取得"""
        if room_id not in self.messages:
            return []
        
        messages = self.messages[room_id]
        
        # 古いメッセージを削除（保持期間を超えた場合）
        cutoff_time = datetime.now() - timedelta(hours=chat_settings.chat_history_retention_hours)
        messages = [msg for msg in messages if msg.timestamp > cutoff_time]
        self.messages[room_id] = messages
        
        if limit:
            return messages[-limit:]
        return messages
    
    def get_chat_history(self, room_id: str, limit: Optional[int] = None) -> ChatHistory:
        """チャット履歴を取得"""
        messages = self.get_messages(room_id, limit)
        return ChatHistory(
            room_id=room_id,
            messages=messages,
            total_messages=len(messages)
        )
    
    def get_room_users(self, room_id: str) -> List[ChatUser]:
        """ルームのユーザー一覧を取得"""
        return [user for user in self.users.values() if user.room_id == room_id]
    
    def get_user_connections(self, room_id: str) -> List[WebSocket]:
        """ルームのWebSocket接続一覧を取得"""
        return [
            self.connections[user_id] 
            for user_id, user in self.users.items() 
            if user.room_id == room_id and user_id in self.connections
        ]
    
    def get_user(self, user_id: str) -> Optional[ChatUser]:
        """ユーザー情報を取得"""
        return self.users.get(user_id)
    
    def cleanup_old_messages(self):
        """古いメッセージをクリーンアップ"""
        cutoff_time = datetime.now() - timedelta(hours=chat_settings.chat_history_retention_hours)
        for room_id in self.messages:
            self.messages[room_id] = [
                msg for msg in self.messages[room_id] 
                if msg.timestamp > cutoff_time
            ]


# グローバルなリポジトリインスタンス
chat_repository = ChatRepository()