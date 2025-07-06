import json

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from template_fastapi.models.chat import (
    ChatHistory,
    ChatRoom,
)
from template_fastapi.repositories.chats import chat_repository
from template_fastapi.settings.chats import get_chat_settings

router = APIRouter()
chat_settings = get_chat_settings()


def _load_chat_html() -> str:
    """チャットHTMLテンプレートを読み込む"""
    try:
        with open(
            "template_fastapi/templates/chat.html",
            encoding="utf-8",
        ) as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
        <head><title>Chat Error</title></head>
        <body>
        <h1>Chat template not found</h1>
        <p>The chat template file could not be loaded.</p>
        </body>
        </html>
        """


@router.get("/chats/", response_class=HTMLResponse, tags=["chats"], operation_id="get_chat_page")
async def get_chat_page():
    """
    チャットページを表示
    """
    return _load_chat_html()


@router.get("/chats/rooms/", response_model=list[ChatRoom], tags=["chats"], operation_id="list_chat_rooms")
async def list_chat_rooms():
    """
    チャットルーム一覧を取得
    """
    return chat_repository.list_rooms()


@router.get("/chats/rooms/{room_id}", response_model=ChatRoom, tags=["chats"], operation_id="get_chat_room")
async def get_chat_room(room_id: str):
    """
    チャットルーム情報を取得
    """
    room = chat_repository.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.get(
    "/chats/rooms/{room_id}/history", response_model=ChatHistory, tags=["chats"], operation_id="get_chat_history"
)
async def get_chat_history(room_id: str, limit: int | None = Query(None, description="取得するメッセージ数の上限")):
    """
    チャットルームの履歴を取得
    """
    room = chat_repository.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    return chat_repository.get_chat_history(room_id, limit)


@router.post("/chats/rooms/", response_model=ChatRoom, tags=["chats"], operation_id="create_chat_room")
async def create_chat_room(room_id: str, name: str, description: str | None = None):
    """
    新しいチャットルームを作成
    """
    try:
        return chat_repository.create_room(room_id, name, description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.websocket("/ws/chats/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    user_id: str = Query(..., description="ユーザーID"),
    username: str = Query(..., description="ユーザー名"),
):
    """
    チャットWebSocketエンドポイント
    """
    await websocket.accept()

    try:
        # バリデーション
        if not username or len(username) > chat_settings.chat_max_username_length:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"ユーザー名は1文字以上{chat_settings.chat_max_username_length}文字以内で入力してください",  # noqa: E501
                    }
                )
            )
            await websocket.close()
            return

        # ルームが存在しない場合は作成
        room = chat_repository.get_room(room_id)
        if not room:
            chat_repository.create_room(room_id, f"Room {room_id}", f"Chat room {room_id}")

        # ユーザーをルームに参加させる
        _ = chat_repository.join_room(user_id, username, room_id, websocket)

        # 既存のメッセージ履歴を送信
        history = chat_repository.get_chat_history(room_id, chat_settings.chat_max_history_messages)
        await websocket.send_text(
            json.dumps({"type": "history", "messages": [msg.model_dump() for msg in history.messages]})
        )

        # 他のユーザーに参加通知
        room_connections = chat_repository.get_user_connections(room_id)
        join_message = {
            "type": "user_joined",
            "username": username,
            "user_count": len(chat_repository.get_room_users(room_id)),
        }

        for connection in room_connections:
            if connection != websocket:
                try:
                    await connection.send_text(json.dumps(join_message))
                except:  # noqa: E722
                    pass

        # メッセージループ
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)

                if message_data.get("type") == "message":
                    message_text = message_data.get("message", "").strip()

                    # メッセージのバリデーション
                    if not message_text:
                        continue

                    if len(message_text) > chat_settings.chat_max_message_length:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "error",
                                    "message": f"メッセージは{chat_settings.chat_max_message_length}文字以内で入力してください",  # noqa: E501
                                }
                            )
                        )
                        continue

                    # メッセージを保存
                    chat_message = chat_repository.add_message(user_id, message_text, room_id)

                    # ルームの全ユーザーにメッセージを送信
                    room_connections = chat_repository.get_user_connections(room_id)
                    message_payload = {"type": "message", "message": chat_message.model_dump()}

                    for connection in room_connections:
                        try:
                            await connection.send_text(json.dumps(message_payload))
                        except:  # noqa: E722
                            pass

            except WebSocketDisconnect:
                break
            except Exception as e:
                # エラーをログに記録（実際の実装では適切なロギング）
                print(f"WebSocket error: {e}")
                break

    except Exception as e:
        print(f"WebSocket setup error: {e}")
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": "接続エラーが発生しました"}))
        except:  # noqa: E722
            pass

    finally:
        # ユーザーをルームから退出
        try:
            old_user = chat_repository.get_user(user_id)
            if old_user:
                chat_repository.leave_room(user_id)

                # 他のユーザーに退出通知
                room_connections = chat_repository.get_user_connections(room_id)
                leave_message = {
                    "type": "user_left",
                    "username": old_user.username,
                    "user_count": len(chat_repository.get_room_users(room_id)),
                }

                for connection in room_connections:
                    try:
                        await connection.send_text(json.dumps(leave_message))
                    except:  # noqa: E722
                        pass
        except:  # noqa: E722
            pass


@router.delete("/chats/rooms/{room_id}/messages", tags=["chats"], operation_id="clear_chat_history")
async def clear_chat_history(room_id: str):
    """
    チャットルームの履歴をクリア
    """
    room = chat_repository.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # メッセージ履歴をクリア
    chat_repository.messages[room_id] = []

    return {"message": f"Chat history for room {room_id} cleared successfully"}


@router.post("/chats/cleanup", tags=["chats"], operation_id="cleanup_old_messages")
async def cleanup_old_messages():
    """
    古いメッセージをクリーンアップ
    """
    chat_repository.cleanup_old_messages()
    return {"message": "Old messages cleaned up successfully"}
