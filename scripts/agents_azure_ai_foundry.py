import json

import typer
from rich.console import Console
from rich.table import Table

from template_fastapi.models.agent import AgentRequest, ChatRequest
from template_fastapi.repositories.agents import AgentRepository

app = typer.Typer()
console = Console()
agent_repo = AgentRepository()


@app.command()
def create_agent(
    name: str = typer.Argument(..., help="エージェント名"),
    description: str | None = typer.Option(None, "--description", "-d", help="エージェントの説明"),
    instructions: str | None = typer.Option(None, "--instructions", "-i", help="エージェントの指示"),
    model: str = typer.Option("gpt-4o", "--model", "-m", help="使用するモデル"),
):
    """新しいエージェントを作成する"""
    console.print("[bold green]新しいエージェントを作成します[/bold green]")
    console.print(f"名前: {name}")
    console.print(f"説明: {description or 'なし'}")
    console.print(f"指示: {instructions or 'なし'}")
    console.print(f"モデル: {model}")

    try:
        request = AgentRequest(
            name=name,
            description=description,
            instructions=instructions,
            model=model,
        )

        agent = agent_repo.create_agent(request)

        console.print("\n[bold blue]エージェントが正常に作成されました[/bold blue]:")
        console.print(f"ID: {agent.id}")
        console.print(f"名前: {agent.name}")
        console.print(f"説明: {agent.description}")
        console.print(f"指示: {agent.instructions}")
        console.print(f"モデル: {agent.model}")
        console.print(f"ステータス: {agent.status}")
        console.print(f"作成日時: {agent.created_at}")

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def get_agent(
    agent_id: str = typer.Argument(..., help="エージェントID"),
):
    """エージェントの情報を取得する"""
    console.print("[bold green]エージェント情報を取得します[/bold green]")
    console.print(f"エージェントID: {agent_id}")

    try:
        agent = agent_repo.get_agent(agent_id)

        console.print("\n[bold blue]エージェント情報[/bold blue]:")
        console.print(f"ID: {agent.id}")
        console.print(f"名前: {agent.name}")
        console.print(f"説明: {agent.description}")
        console.print(f"指示: {agent.instructions}")
        console.print(f"モデル: {agent.model}")
        console.print(f"ステータス: {agent.status}")
        console.print(f"作成日時: {agent.created_at}")
        console.print(f"更新日時: {agent.updated_at}")

        if agent.tools:
            console.print(f"ツール: {json.dumps(agent.tools, indent=2, ensure_ascii=False)}")

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def list_agents(
    limit: int = typer.Option(10, "--limit", "-l", help="取得する件数"),
):
    """エージェントの一覧を取得する"""
    console.print("[bold green]エージェント一覧を取得します[/bold green]")
    console.print(f"取得件数: {limit}")

    try:
        agents_response = agent_repo.list_agents(limit=limit)

        if not agents_response.agents:
            console.print("[yellow]エージェントが見つかりません[/yellow]")
            return

        table = Table(title="エージェント一覧")
        table.add_column("ID", style="cyan")
        table.add_column("名前", style="magenta")
        table.add_column("説明", style="green")
        table.add_column("モデル", style="blue")
        table.add_column("ステータス", style="yellow")
        table.add_column("作成日時", style="dim")

        for agent in agents_response.agents:
            table.add_row(
                agent.id,
                agent.name,
                agent.description or "なし",
                agent.model,
                agent.status,
                agent.created_at,
            )

        console.print(table)
        console.print(f"[bold blue]合計: {agents_response.total}件[/bold blue]")

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def delete_agent(
    agent_id: str = typer.Argument(..., help="エージェントID"),
):
    """エージェントを削除する"""
    console.print("[bold red]エージェントを削除します[/bold red]")
    console.print(f"エージェントID: {agent_id}")

    confirm = typer.confirm("本当に削除しますか？")
    if not confirm:
        console.print("[yellow]削除をキャンセルしました[/yellow]")
        return

    try:
        success = agent_repo.delete_agent(agent_id)

        if success:
            console.print("[bold green]エージェントが正常に削除されました[/bold green]")
        else:
            console.print("[bold red]エージェントの削除に失敗しました[/bold red]")

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def chat(
    agent_id: str = typer.Argument(..., help="エージェントID"),
    message: str = typer.Argument(..., help="メッセージ"),
    thread_id: str | None = typer.Option(None, "--thread-id", "-t", help="スレッドID"),
):
    """エージェントとチャットする"""
    console.print("[bold green]エージェントとチャットします[/bold green]")
    console.print(f"エージェントID: {agent_id}")
    console.print(f"メッセージ: {message}")
    console.print(f"スレッドID: {thread_id or '新規作成'}")

    try:
        request = ChatRequest(
            message=message,
            thread_id=thread_id,
        )

        response = agent_repo.chat_with_agent(agent_id, request)

        console.print("\n[bold blue]チャット結果[/bold blue]:")
        console.print(f"メッセージID: {response.id}")
        console.print(f"スレッドID: {response.thread_id}")
        console.print(f"あなた: {response.message}")
        console.print(f"エージェント: {response.response}")
        console.print(f"作成日時: {response.created_at}")

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


if __name__ == "__main__":
    app()
