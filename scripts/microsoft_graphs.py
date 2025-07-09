#!/usr/bin/env python

import asyncio

import typer
from azure.core.credentials import AccessToken
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from rich.console import Console
from rich.table import Table

from template_fastapi.settings.microsoft_graphs import get_microsoft_graph_settings

app = typer.Typer()
console = Console()


class RawAccessTokenProvider:
    def __init__(self, access_token: str, expires_on: int):
        self._access_token = access_token
        self._expires_on = expires_on

    def get_token(self, *scopes, **kwargs) -> AccessToken:
        return AccessToken(self._access_token, self._expires_on)


def get_graph_client(
    access_token: str | None = None,
    expires_on: int | None = None,
) -> GraphServiceClient:
    """Microsoft Graph クライアントを取得する"""
    settings = get_microsoft_graph_settings()
    scopes = settings.microsoft_graph_user_scopes.split(" ")

    if access_token and expires_on:
        # アクセストークンが指定されている場合はそれを使用
        access_token_provider = RawAccessTokenProvider(access_token, expires_on)
        return GraphServiceClient(credentials=access_token_provider, scopes=scopes)
    device_code_credential = DeviceCodeCredential(
        client_id=settings.microsoft_graph_client_id,
        tenant_id=settings.microsoft_graph_tenant_id,
    )
    return GraphServiceClient(
        credentials=device_code_credential,
        scopes=scopes,
    )


@app.command()
def get_my_profile(
    fields: list[str] | None = typer.Option(None, "--field", "-f", help="取得するフィールドを指定（複数指定可能）"),
    access_token: str | None = typer.Option(None, "--access-token", "-a", help="アクセストークンを指定して認証する"),
    expires_on: int | None = typer.Option(
        None, "--expires-on", "-e", help="アクセストークンの有効期限を指定（Unix時間）"
    ),
):
    """自分のプロファイル情報を取得する"""
    console.print("[bold green]ユーザープロファイル[/bold green]を取得します")

    # デフォルトのフィールド
    default_fields = ["displayName", "mail", "userPrincipalName", "id", "jobTitle", "department"]
    select_fields = fields or default_fields

    async def _get_profile():
        try:
            client = get_graph_client(access_token=access_token, expires_on=expires_on)

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

        print(f"access_token: {access_token.token}")
        print(f"expires_on: {access_token.expires_on}")

    except Exception as e:
        console.print(f"[bold red]エラー[/bold red]: {str(e)}")


@app.command()
def get_sites(
    site_id: str | None = typer.Option(None, "--site-id", "-s", help="取得するサイトの ID（省略時は全サイト）"),
    access_token: str | None = typer.Option(None, "--access-token", "-a", help="アクセストークンを指定して認証する"),
    expires_on: int | None = typer.Option(
        None, "--expires-on", "-e", help="アクセストークンの有効期限を指定（Unix時間）"
    ),
):
    """SharePoint サイトの情報を取得する"""
    console.print("[bold green]SharePoint サイト[/bold green]の情報を取得します")

    async def _get_sites():
        try:
            client = get_graph_client(access_token=access_token, expires_on=expires_on)

            if site_id:
                site = await client.sites.by_site_id(site_id).get()
                sites = [site]
            else:
                sites_response = await client.sites.get()
                sites = sites_response.value if sites_response.value else []

            # テーブルで表示
            table = Table(title="SharePoint サイト")
            table.add_column("ID", style="cyan")
            table.add_column("名前", style="green")
            table.add_column("URL", style="blue")

            for site in sites:
                table.add_row(site.id, site.name, site.web_url)

            console.print(table)

        except Exception as e:
            console.print(f"[bold red]エラー[/bold red]: {str(e)}")

    asyncio.run(_get_sites())


if __name__ == "__main__":
    app()
