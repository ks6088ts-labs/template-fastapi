#!/usr/bin/env python

import asyncio

import typer
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from rich.console import Console
from rich.table import Table

from template_fastapi.settings.microsoft_graphs import get_microsoft_graph_settings

app = typer.Typer()
console = Console()


def get_graph_client() -> tuple[GraphServiceClient, list[str]]:
    """Microsoft Graph クライアントを取得する"""
    settings = get_microsoft_graph_settings()
    scopes = settings.microsoft_graph_user_scopes.split(" ")

    device_code_credential = DeviceCodeCredential(
        client_id=settings.microsoft_graph_client_id,
        tenant_id=settings.microsoft_graph_tenant_id,
    )

    client = GraphServiceClient(
        credentials=device_code_credential,
        scopes=scopes,
    )

    return client, scopes


@app.command()
def get_my_profile(
    fields: list[str] | None = typer.Option(None, "--field", "-f", help="取得するフィールドを指定（複数指定可能）"),
):
    """自分のプロファイル情報を取得する"""
    console.print("[bold green]ユーザープロファイル[/bold green]を取得します")

    # デフォルトのフィールド
    default_fields = ["displayName", "mail", "userPrincipalName", "id", "jobTitle", "department"]
    select_fields = fields or default_fields

    async def _get_profile():
        try:
            client, _ = get_graph_client()

            query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(select=select_fields)
            request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
                query_parameters=query_params
            )

            user = await client.me.get(request_configuration=request_config)

            # テーブルで表示
            table = Table(title="ユーザープロファイル")
            table.add_column("項目", style="cyan")
            table.add_column("値", style="green")

            # 動的にフィールドを表示
            for field in select_fields:
                value = getattr(user, field.replace("_", ""), "N/A")
                if value is not None:
                    table.add_row(field, str(value))

            console.print(table)

        except Exception as e:
            console.print(f"[bold red]エラー[/bold red]: {str(e)}")

    asyncio.run(_get_profile())


@app.command()
def get_access_token():
    """アクセストークンを取得する"""
    console.print("[bold green]アクセストークン[/bold green]を取得します")

    try:
        settings = get_microsoft_graph_settings()
        scopes = settings.microsoft_graph_user_scopes.split(" ")

        device_code_credential = DeviceCodeCredential(
            client_id=settings.microsoft_graph_client_id,
            tenant_id=settings.microsoft_graph_tenant_id,
        )

        access_token = device_code_credential.get_token(*scopes)

        console.print("[bold green]トークン取得成功[/bold green]")
        console.print(f"  トークン: {access_token.token}")
        console.print(f"  期限: {access_token.expires_on}")

    except Exception as e:
        console.print(f"[bold red]エラー[/bold red]: {str(e)}")


if __name__ == "__main__":
    app()
