#!/usr/bin/env python
# filepath: /home/runner/work/template-fastapi/template-fastapi/scripts/chats.py


import typer
from rich.console import Console
from rich.table import Table

from template_fastapi.repositories.chats import chat_repository

app = typer.Typer()
console = Console()


@app.command()
def list_rooms():
    """チャットルーム一覧を表示"""
    console.print("[bold green]チャットルーム一覧[/bold green]")

    rooms = chat_repository.list_rooms()

    if not rooms:
        console.print("[yellow]チャットルームが見つかりませんでした[/yellow]")
        return

    table = Table(title="チャットルーム")
    table.add_column("ルームID", style="cyan")
    table.add_column("名前", style="green")
    table.add_column("説明", style="blue")
    table.add_column("ユーザー数", style="yellow")
    table.add_column("作成日時", style="magenta")

    for room in rooms:
        table.add_row(
            room.room_id,
            room.name,
            room.description or "N/A",
            str(room.user_count),
            room.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    console.print(table)


@app.command()
def create_room(
    room_id: str = typer.Argument(..., help="ルームID"),
    name: str = typer.Argument(..., help="ルーム名"),
    description: str = typer.Option(None, "--description", "-d", help="ルーム説明"),
):
    """新しいチャットルームを作成"""
    console.print(f"[bold green]チャットルーム '{room_id}' を作成します[/bold green]")

    try:
        room = chat_repository.create_room(room_id, name, description)
        console.print("✅ [bold green]チャットルームが正常に作成されました[/bold green]")
        console.print(f"ルームID: {room.room_id}")
        console.print(f"名前: {room.name}")
        if room.description:
            console.print(f"説明: {room.description}")
        console.print(f"作成日時: {room.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    except ValueError as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")
    except Exception as e:
        console.print(f"❌ [bold red]予期しないエラー[/bold red]: {str(e)}")


@app.command()
def get_room(room_id: str = typer.Argument(..., help="ルームID")):
    """チャットルーム情報を取得"""
    console.print(f"[bold green]チャットルーム '{room_id}' の情報を取得します[/bold green]")

    room = chat_repository.get_room(room_id)
    if not room:
        console.print(f"❌ [bold red]ルーム '{room_id}' が見つかりません[/bold red]")
        return

    console.print("✅ [bold green]ルーム情報[/bold green]")
    console.print(f"ルームID: {room.room_id}")
    console.print(f"名前: {room.name}")
    console.print(f"説明: {room.description or 'N/A'}")
    console.print(f"ユーザー数: {room.user_count}")
    console.print(f"作成日時: {room.created_at.strftime('%Y-%m-%d %H:%M:%S')}")


@app.command()
def get_history(
    room_id: str = typer.Argument(..., help="ルームID"),
    limit: int = typer.Option(50, "--limit", "-l", help="取得するメッセージ数"),
):
    """チャットルームの履歴を取得"""
    console.print(f"[bold green]チャットルーム '{room_id}' の履歴を取得します[/bold green]")

    room = chat_repository.get_room(room_id)
    if not room:
        console.print(f"❌ [bold red]ルーム '{room_id}' が見つかりません[/bold red]")
        return

    history = chat_repository.get_chat_history(room_id, limit)

    if not history.messages:
        console.print("[yellow]メッセージが見つかりませんでした[/yellow]")
        return

    console.print(f"✅ [bold green]メッセージ履歴 (最新 {len(history.messages)} 件)[/bold green]")
    console.print()

    for message in history.messages:
        timestamp = message.timestamp.strftime("%H:%M:%S")
        console.print(f"[dim]{timestamp}[/dim] [bold cyan]{message.username}[/bold cyan]: {message.message}")


@app.command()
def list_users(room_id: str = typer.Argument(..., help="ルームID")):
    """チャットルームのユーザー一覧を表示"""
    console.print(f"[bold green]チャットルーム '{room_id}' のユーザー一覧[/bold green]")

    room = chat_repository.get_room(room_id)
    if not room:
        console.print(f"❌ [bold red]ルーム '{room_id}' が見つかりません[/bold red]")
        return

    users = chat_repository.get_room_users(room_id)

    if not users:
        console.print("[yellow]参加中のユーザーがいません[/yellow]")
        return

    table = Table(title=f"ルーム '{room_id}' の参加者")
    table.add_column("ユーザーID", style="cyan")
    table.add_column("ユーザー名", style="green")
    table.add_column("参加日時", style="magenta")

    for user in users:
        table.add_row(user.user_id, user.username, user.connected_at.strftime("%Y-%m-%d %H:%M:%S"))

    console.print(table)


@app.command()
def clear_history(
    room_id: str = typer.Argument(..., help="ルームID"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="確認なしで実行"),
):
    """チャットルームの履歴をクリア"""
    if not confirm:
        confirmed = typer.confirm(f"ルーム '{room_id}' のメッセージ履歴をクリアしますか？")
        if not confirmed:
            console.print("[yellow]キャンセルしました[/yellow]")
            return

    room = chat_repository.get_room(room_id)
    if not room:
        console.print(f"❌ [bold red]ルーム '{room_id}' が見つかりません[/bold red]")
        return

    try:
        chat_repository.messages[room_id] = []
        console.print(f"✅ [bold green]ルーム '{room_id}' の履歴をクリアしました[/bold green]")
    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def cleanup():
    """古いメッセージをクリーンアップ"""
    console.print("[bold green]古いメッセージをクリーンアップします[/bold green]")

    try:
        chat_repository.cleanup_old_messages()
        console.print("✅ [bold green]クリーンアップが完了しました[/bold green]")
    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def stats():
    """チャットシステムの統計情報を表示"""
    console.print("[bold green]チャットシステム統計情報[/bold green]")

    rooms = chat_repository.list_rooms()
    total_users = sum(len(chat_repository.get_room_users(room.room_id)) for room in rooms)
    total_messages = sum(len(chat_repository.messages.get(room.room_id, [])) for room in rooms)

    stats_table = Table(title="統計情報")
    stats_table.add_column("項目", style="cyan")
    stats_table.add_column("値", style="green")

    stats_table.add_row("総ルーム数", str(len(rooms)))
    stats_table.add_row("総ユーザー数", str(total_users))
    stats_table.add_row("総メッセージ数", str(total_messages))

    console.print(stats_table)

    if rooms:
        console.print("\n[bold green]ルーム別統計[/bold green]")
        room_table = Table()
        room_table.add_column("ルーム", style="cyan")
        room_table.add_column("ユーザー数", style="yellow")
        room_table.add_column("メッセージ数", style="green")

        for room in rooms:
            user_count = len(chat_repository.get_room_users(room.room_id))
            message_count = len(chat_repository.messages.get(room.room_id, []))
            room_table.add_row(room.name, str(user_count), str(message_count))

        console.print(room_table)


@app.command()
def send_message(
    room_id: str = typer.Argument(..., help="ルームID"),
    username: str = typer.Argument(..., help="ユーザー名"),
    message: str = typer.Argument(..., help="メッセージ"),
):
    """メッセージを送信 (テスト用)"""
    console.print("[bold green]メッセージを送信します[/bold green]")

    room = chat_repository.get_room(room_id)
    if not room:
        console.print(f"❌ [bold red]ルーム '{room_id}' が見つかりません[/bold red]")
        return

    try:
        # テスト用の一時的なユーザーを作成
        import uuid

        from template_fastapi.models.chat import ChatUser

        user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        test_user = ChatUser(user_id=user_id, username=username, room_id=room_id)
        chat_repository.users[user_id] = test_user

        # メッセージを追加
        chat_message = chat_repository.add_message(user_id, message, room_id)

        console.print("✅ [bold green]メッセージが送信されました[/bold green]")
        console.print(f"ユーザー: {chat_message.username}")
        console.print(f"メッセージ: {chat_message.message}")
        console.print(f"時刻: {chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        # テスト用ユーザーを削除
        del chat_repository.users[user_id]

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


if __name__ == "__main__":
    app()
