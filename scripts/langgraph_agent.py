#!/usr/bin/env python
# filepath: /home/runner/work/template-fastapi/template-fastapi/scripts/langgraph_agent.py

"""LangGraph Agent CLI tool."""

import json
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from template_fastapi.core.langgraph.agent import LangGraphAgent
from template_fastapi.core.langgraph.tools import get_tools

app = typer.Typer()
console = Console()


@app.command()
def chat(
    message: str = typer.Argument(..., help="メッセージ"),
    thread_id: Optional[str] = typer.Option(None, "--thread-id", "-t", help="スレッドID（会話の継続用）"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="詳細な情報を表示"),
):
    """LangGraphエージェントとチャットする"""
    console.print("[bold green]LangGraphエージェントとチャットします[/bold green]")
    console.print(f"メッセージ: {message}")
    
    if thread_id:
        console.print(f"スレッドID: {thread_id}")
    else:
        console.print("新しいスレッドを作成します")
    
    try:
        # Initialize the LangGraph agent
        agent = LangGraphAgent()
        
        # Show loading message
        with console.status("[bold green]エージェントが応答を生成中...", spinner="dots"):
            result = agent.chat(message=message, thread_id=thread_id)
        
        # Display results
        console.print("\n" + "="*50)
        console.print("[bold blue]チャット結果[/bold blue]")
        console.print("="*50)
        
        # Display user message
        user_panel = Panel(
            message,
            title="[bold cyan]あなた[/bold cyan]",
            border_style="cyan"
        )
        console.print(user_panel)
        
        # Display agent response with markdown rendering
        response_content = result["response"]
        if response_content:
            try:
                # Try to render as markdown for better formatting
                markdown = Markdown(response_content)
                agent_panel = Panel(
                    markdown,
                    title="[bold green]LangGraphエージェント[/bold green]",
                    border_style="green"
                )
            except Exception:
                # Fallback to plain text
                agent_panel = Panel(
                    response_content,
                    title="[bold green]LangGraphエージェント[/bold green]",
                    border_style="green"
                )
            console.print(agent_panel)
        
        # Display metadata
        if verbose:
            console.print("\n[bold yellow]メタデータ[/bold yellow]:")
            console.print(f"スレッドID: {result['thread_id']}")
            console.print(f"作成日時: {result['created_at']}")
            console.print(f"ステップ数: {result.get('step_count', 0)}")
            
            if result.get("tools_used"):
                console.print(f"使用ツール: {', '.join(result['tools_used'])}")
            else:
                console.print("使用ツール: なし")
        else:
            console.print(f"\n[dim]スレッドID: {result['thread_id']}[/dim]")
            if result.get("tools_used"):
                console.print(f"[dim]使用ツール: {', '.join(result['tools_used'])}[/dim]")
                
    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def interactive():
    """対話モードでLangGraphエージェントとチャットする"""
    console.print("[bold green]LangGraphエージェント対話モード[/bold green]")
    console.print("終了するには 'exit', 'quit', または 'bye' と入力してください\n")
    
    agent = LangGraphAgent()
    thread_id = None
    
    while True:
        try:
            # Get user input
            user_input = typer.prompt("あなた")
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'bye', '終了']:
                console.print("[yellow]対話を終了します。ありがとうございました！[/yellow]")
                break
            
            # Process the message
            with console.status("[bold green]応答を生成中...", spinner="dots"):
                result = agent.chat(message=user_input, thread_id=thread_id)
            
            # Update thread_id for conversation continuity
            thread_id = result["thread_id"]
            
            # Display agent response
            response_panel = Panel(
                Markdown(result["response"]) if result["response"] else "応答がありません",
                title="[bold green]エージェント[/bold green]",
                border_style="green"
            )
            console.print(response_panel)
            
            # Show tools used if any
            if result.get("tools_used"):
                console.print(f"[dim]使用ツール: {', '.join(result['tools_used'])}[/dim]")
            
            console.print()  # Add spacing
            
        except KeyboardInterrupt:
            console.print("\n[yellow]対話を終了します[/yellow]")
            break
        except Exception as e:
            console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def tools():
    """利用可能なツールの一覧を表示する"""
    console.print("[bold green]利用可能なツール一覧[/bold green]")
    
    try:
        available_tools = get_tools()
        
        if not available_tools:
            console.print("[yellow]利用可能なツールがありません[/yellow]")
            return
        
        console.print(f"\n[bold blue]合計 {len(available_tools)} 個のツールが利用可能です[/bold blue]\n")
        
        for i, tool in enumerate(available_tools, 1):
            tool_info = f"""
**名前:** {tool.name}
**説明:** {tool.description}
"""
            if hasattr(tool, 'args_schema') and tool.args_schema:
                try:
                    schema = tool.args_schema.model_json_schema()
                    if 'properties' in schema:
                        tool_info += f"**パラメータ:** {', '.join(schema['properties'].keys())}"
                except Exception:
                    pass
            
            panel = Panel(
                Markdown(tool_info),
                title=f"[bold cyan]ツール {i}[/bold cyan]",
                border_style="cyan"
            )
            console.print(panel)
            
    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def demo():
    """デモンストレーション用のサンプルチャット"""
    console.print("[bold green]LangGraphエージェント デモモード[/bold green]")
    console.print("いくつかのサンプル質問でエージェントをテストします\n")
    
    sample_queries = [
        "こんにちは！今何時ですか？",
        "2 + 2 × 3 を計算してください",
        "Pythonについて検索してください",
    ]
    
    agent = LangGraphAgent()
    
    for i, query in enumerate(sample_queries, 1):
        console.print(f"[bold yellow]サンプル質問 {i}:[/bold yellow] {query}")
        
        try:
            with console.status(f"[bold green]質問 {i} を処理中...", spinner="dots"):
                result = agent.chat(message=query)
            
            response_panel = Panel(
                Markdown(result["response"]) if result["response"] else "応答がありません",
                title="[bold green]エージェントの応答[/bold green]",
                border_style="green"
            )
            console.print(response_panel)
            
            if result.get("tools_used"):
                console.print(f"[dim]使用ツール: {', '.join(result['tools_used'])}[/dim]")
            
            console.print()  # Add spacing
            
        except Exception as e:
            console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")
            console.print()


if __name__ == "__main__":
    app()