from fastapi import WebSocket


class ConnectionManager:
    """WebSocket connection manager for handling multiple client connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a WebSocket connection and add it to active connections."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from active connections."""
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a personal message to a specific WebSocket connection."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Broadcast a message to all active connections."""
        for connection in self.active_connections:
            await connection.send_text(message)


class ChatRepository:
    """Repository for handling chat-related operations."""

    def __init__(self):
        self.manager = ConnectionManager()

    async def handle_client_message(self, data: str, websocket: WebSocket, client_id: int):
        """Handle a message from a client."""
        # await self.manager.send_personal_message(f"You wrote: {data}", websocket)

        # client_id が一致する client 以外にのみ data を送信する
        for connection in self.manager.active_connections:
            if connection != websocket:
                await self.manager.send_personal_message(f"Client #{client_id} says: {data}", connection)

        # もし全クライアントにブロードキャストしたい場合は以下の行を有効にしてください
        # await self.manager.broadcast(f"Client #{client_id} says: {data}")

    async def handle_client_disconnect(self, client_id: int):
        """Handle a client disconnect."""
        await self.manager.broadcast(f"Client #{client_id} left the chat")
