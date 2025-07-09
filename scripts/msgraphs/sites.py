#!/usr/bin/env python
# filepath: /home/runner/work/template-fastapi/template-fastapi/scripts/msgraphs/sites.py

import json
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from template_fastapi.repositories.msgraphs import MicrosoftGraphRepository

app = typer.Typer()
console = Console()
msgraphs_repo = MicrosoftGraphRepository()


@app.command()
def list_files(
    site_id: str = typer.Argument(..., help="SharePoint Site ID"),
    folder: str = typer.Option("", help="フォルダパス（省略時はルートディレクトリ）"),
    format: str = typer.Option("table", help="出力形式 (table/json)"),
) -> None:
    """SharePointサイトのファイル一覧を表示する"""
    try:
        files = msgraphs_repo.sites.list_files(site_id, folder)

        if format == "json":
            files_data = [
                {
                    "name": file.name,
                    "size": file.size,
                    "content_type": file.content_type,
                    "created_at": file.created_at.isoformat() if file.created_at else None,
                    "updated_at": file.updated_at.isoformat() if file.updated_at else None,
                }
                for file in files
            ]
            console.print(json.dumps(files_data, indent=2))
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ファイル名", style="cyan")
            table.add_column("サイズ", justify="right")
            table.add_column("タイプ", style="green")
            table.add_column("作成日時", style="blue")
            table.add_column("更新日時", style="blue")

            for file in files:
                size_str = f"{file.size:,} bytes" if file.size else "不明"
                created_str = file.created_at.strftime("%Y-%m-%d %H:%M:%S") if file.created_at else "不明"
                updated_str = file.updated_at.strftime("%Y-%m-%d %H:%M:%S") if file.updated_at else "不明"

                table.add_row(
                    file.name,
                    size_str,
                    file.content_type,
                    created_str,
                    updated_str,
                )

            console.print(table)

        console.print(f"\n📁 フォルダ: {folder if folder else 'ルート'}")
        console.print(f"📄 ファイル数: {len(files)}")

    except Exception as e:
        console.print(f"❌ エラー: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def upload_file(
    site_id: str = typer.Argument(..., help="SharePoint Site ID"),
    file_path: str = typer.Argument(..., help="アップロードするファイルのパス"),
    folder: str = typer.Option("", help="アップロード先のフォルダパス"),
) -> None:
    """SharePointサイトにファイルをアップロードする"""
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            console.print(f"❌ ファイルが見つかりません: {file_path}", style="bold red")
            raise typer.Exit(1)

        with open(file_path_obj, "rb") as f:
            file_content = f.read()

        uploaded_file = msgraphs_repo.sites.upload_file(site_id, file_content, file_path_obj.name, folder)

        console.print(f"✅ ファイルをアップロードしました: {uploaded_file.name}", style="bold green")
        console.print(f"📁 フォルダ: {folder if folder else 'ルート'}")
        console.print(f"📄 サイズ: {uploaded_file.size:,} bytes")

    except Exception as e:
        console.print(f"❌ エラー: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def upload_files(
    site_id: str = typer.Argument(..., help="SharePoint Site ID"),
    file_paths: list[str] = typer.Argument(..., help="アップロードするファイルのパス（複数指定可能）"),
    folder: str = typer.Option("", help="アップロード先のフォルダパス"),
) -> None:
    """SharePointサイトに複数のファイルを同時にアップロードする"""
    try:
        files_data = []
        for file_path in file_paths:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                console.print(f"❌ ファイルが見つかりません: {file_path}", style="bold red")
                continue

            with open(file_path_obj, "rb") as f:
                file_content = f.read()
            files_data.append((file_content, file_path_obj.name))

        if not files_data:
            console.print("❌ 有効なファイルがありません", style="bold red")
            raise typer.Exit(1)

        uploaded_files = msgraphs_repo.sites.upload_multiple_files(site_id, files_data, folder)

        console.print(f"✅ {len(uploaded_files)}個のファイルをアップロードしました:", style="bold green")
        for file in uploaded_files:
            console.print(f"  📄 {file.name} ({file.size:,} bytes)")
        console.print(f"📁 フォルダ: {folder if folder else 'ルート'}")

    except Exception as e:
        console.print(f"❌ エラー: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def download_file(
    site_id: str = typer.Argument(..., help="SharePoint Site ID"),
    file_name: str = typer.Argument(..., help="ダウンロードするファイル名"),
    folder: str = typer.Option("", help="ファイルがあるフォルダパス"),
    output: str = typer.Option("", help="出力ファイルパス（省略時はファイル名を使用）"),
) -> None:
    """SharePointサイトからファイルをダウンロードする"""
    try:
        file_content = msgraphs_repo.sites.download_file(site_id, file_name, folder)

        output_path = Path(output) if output else Path(file_name)
        with open(output_path, "wb") as f:
            f.write(file_content)

        console.print(f"✅ ファイルをダウンロードしました: {output_path}", style="bold green")
        console.print(f"📁 フォルダ: {folder if folder else 'ルート'}")
        console.print(f"📄 サイズ: {len(file_content):,} bytes")

    except Exception as e:
        console.print(f"❌ エラー: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def delete_file(
    site_id: str = typer.Argument(..., help="SharePoint Site ID"),
    file_name: str = typer.Argument(..., help="削除するファイル名"),
    folder: str = typer.Option("", help="ファイルがあるフォルダパス"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除する"),
) -> None:
    """SharePointサイトからファイルを削除する"""
    try:
        if not force:
            confirm = typer.confirm(f"ファイル '{file_name}' を削除しますか？")
            if not confirm:
                console.print("削除をキャンセルしました", style="yellow")
                return

        success = msgraphs_repo.sites.delete_file(site_id, file_name, folder)

        if success:
            console.print(f"✅ ファイルを削除しました: {file_name}", style="bold green")
            console.print(f"📁 フォルダ: {folder if folder else 'ルート'}")
        else:
            console.print(f"❌ ファイルの削除に失敗しました: {file_name}", style="bold red")

    except Exception as e:
        console.print(f"❌ エラー: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def delete_files(
    site_id: str = typer.Argument(..., help="SharePoint Site ID"),
    file_names: list[str] = typer.Argument(..., help="削除するファイル名（複数指定可能）"),
    folder: str = typer.Option("", help="ファイルがあるフォルダパス"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除する"),
) -> None:
    """SharePointサイトから複数のファイルを削除する"""
    try:
        if not force:
            console.print(f"削除予定のファイル:")
            for file_name in file_names:
                console.print(f"  📄 {file_name}")
            confirm = typer.confirm(f"{len(file_names)}個のファイルを削除しますか？")
            if not confirm:
                console.print("削除をキャンセルしました", style="yellow")
                return

        deleted_files = msgraphs_repo.sites.delete_multiple_files(site_id, file_names, folder)

        console.print(f"✅ {len(deleted_files)}個のファイルを削除しました:", style="bold green")
        for file_name in deleted_files:
            console.print(f"  📄 {file_name}")
        console.print(f"📁 フォルダ: {folder if folder else 'ルート'}")

        failed_count = len(file_names) - len(deleted_files)
        if failed_count > 0:
            console.print(f"⚠️  {failed_count}個のファイルの削除に失敗しました", style="yellow")

    except Exception as e:
        console.print(f"❌ エラー: {e}", style="bold red")
        raise typer.Exit(1)


@app.command()
def get_file_info(
    site_id: str = typer.Argument(..., help="SharePoint Site ID"),
    file_name: str = typer.Argument(..., help="情報を取得するファイル名"),
    folder: str = typer.Option("", help="ファイルがあるフォルダパス"),
) -> None:
    """SharePointサイトのファイル情報を取得する"""
    try:
        file_info = msgraphs_repo.sites.get_file_info(site_id, file_name, folder)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("項目", style="cyan")
        table.add_column("値", style="white")

        table.add_row("ファイル名", file_info.name)
        table.add_row("サイズ", f"{file_info.size:,} bytes" if file_info.size else "不明")
        table.add_row("タイプ", file_info.content_type)
        table.add_row("作成日時", file_info.created_at.strftime("%Y-%m-%d %H:%M:%S") if file_info.created_at else "不明")
        table.add_row("更新日時", file_info.updated_at.strftime("%Y-%m-%d %H:%M:%S") if file_info.updated_at else "不明")
        table.add_row("フォルダ", folder if folder else "ルート")

        console.print(table)

    except Exception as e:
        console.print(f"❌ エラー: {e}", style="bold red")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()