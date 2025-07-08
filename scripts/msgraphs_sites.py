#!/usr/bin/env python
# filepath: /home/runner/work/template-fastapi/template-fastapi/scripts/msgraphs_sites.py

import json
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from template_fastapi.repositories.msgraphs_sites import MicrosoftGraphSitesRepository

app = typer.Typer()
console = Console()
msgraphs_sites_repo = MicrosoftGraphSitesRepository()


@app.command()
def list_files(
    folder_path: str = typer.Option("", "--folder", "-f", help="フォルダパス"),
    output_format: str = typer.Option("table", "--format", "-o", help="出力形式 (table/json)"),
):
    """SharePointサイトのファイル一覧を取得する"""
    console.print("[bold green]SharePointサイトのファイル一覧を取得します[/bold green]")
    
    try:
        files = msgraphs_sites_repo.list_files(folder_path)
        
        if output_format == "json":
            # JSON形式で出力
            files_json = [
                {
                    "name": file.name,
                    "size": file.size,
                    "content_type": file.content_type,
                    "last_modified": file.last_modified.isoformat() if file.last_modified else None,
                    "url": file.url,
                }
                for file in files
            ]
            console.print(json.dumps(files_json, indent=2, ensure_ascii=False))
        else:
            # テーブル形式で出力
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("ファイル名", style="cyan")
            table.add_column("サイズ", justify="right")
            table.add_column("コンテンツタイプ", style="yellow")
            table.add_column("最終更新日", style="green")
            
            for file in files:
                table.add_row(
                    file.name,
                    str(file.size) if file.size else "N/A",
                    file.content_type or "N/A",
                    file.last_modified.strftime("%Y-%m-%d %H:%M:%S") if file.last_modified else "N/A",
                )
            
            console.print(table)
        
        console.print(f"✅ [bold green]{len(files)} 個のファイルを取得しました[/bold green]")
        
    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def upload_file(
    file_path: str = typer.Argument(..., help="アップロードするファイルのパス"),
    folder_path: str = typer.Option("", "--folder", "-f", help="アップロード先フォルダパス"),
    name: str = typer.Option(None, "--name", "-n", help="アップロード後のファイル名"),
):
    """SharePointサイトにファイルをアップロードする"""
    console.print("[bold green]SharePointサイトにファイルをアップロードします[/bold green]")
    
    try:
        # ファイルの存在確認
        if not os.path.exists(file_path):
            console.print(f"❌ [bold red]エラー[/bold red]: ファイル '{file_path}' が見つかりません")
            return
        
        # ファイルを読み込み
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        # アップロード後のファイル名を決定
        upload_name = name if name else Path(file_path).name
        
        console.print(f"ファイルパス: {file_path}")
        console.print(f"フォルダパス: {folder_path}")
        console.print(f"アップロード名: {upload_name}")
        
        # ファイルをアップロード
        uploaded_file = msgraphs_sites_repo.upload_file(upload_name, file_data, folder_path)
        
        console.print("✅ [bold green]ファイルが正常にアップロードされました[/bold green]")
        console.print(f"ファイル名: {uploaded_file.name}")
        console.print(f"サイズ: {uploaded_file.size} bytes")
        console.print(f"URL: {uploaded_file.url}")
        
    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def upload_files(
    file_paths: list[str] = typer.Argument(..., help="アップロードするファイルのパス（複数指定可能）"),
    folder_path: str = typer.Option("", "--folder", "-f", help="アップロード先フォルダパス"),
):
    """SharePointサイトに複数のファイルを同時にアップロードする"""
    console.print("[bold green]SharePointサイトに複数のファイルをアップロードします[/bold green]")
    
    try:
        file_data_list = []
        
        # 各ファイルを読み込み
        for file_path in file_paths:
            if not os.path.exists(file_path):
                console.print(f"❌ [bold red]エラー[/bold red]: ファイル '{file_path}' が見つかりません")
                continue
            
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            file_name = Path(file_path).name
            file_data_list.append((file_name, file_data, None))
        
        if not file_data_list:
            console.print("❌ [bold red]エラー[/bold red]: アップロード可能なファイルがありません")
            return
        
        console.print(f"アップロード対象: {len(file_data_list)} 個のファイル")
        console.print(f"フォルダパス: {folder_path}")
        
        # 複数ファイルをアップロード
        uploaded_files = msgraphs_sites_repo.upload_files(file_data_list, folder_path)
        
        console.print(f"✅ [bold green]{len(uploaded_files)} 個のファイルが正常にアップロードされました[/bold green]")
        
        # 結果を表示
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("ファイル名", style="cyan")
        table.add_column("サイズ", justify="right")
        table.add_column("URL", style="yellow")
        
        for file in uploaded_files:
            table.add_row(
                file.name,
                str(file.size) if file.size else "N/A",
                file.url or "N/A",
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def download_file(
    file_name: str = typer.Argument(..., help="ダウンロードするファイル名"),
    folder_path: str = typer.Option("", "--folder", "-f", help="ファイルが保存されているフォルダパス"),
    output_path: str = typer.Option("", "--output", "-o", help="保存先パス"),
):
    """SharePointサイトからファイルをダウンロードする"""
    console.print("[bold green]SharePointサイトからファイルをダウンロードします[/bold green]")
    
    try:
        console.print(f"ファイル名: {file_name}")
        console.print(f"フォルダパス: {folder_path}")
        
        # ファイルをダウンロード
        file_data = msgraphs_sites_repo.download_file(file_name, folder_path)
        
        # 保存先パスを決定
        save_path = output_path if output_path else file_name
        
        # ファイルを保存
        with open(save_path, "wb") as f:
            f.write(file_data)
        
        console.print("✅ [bold green]ファイルが正常にダウンロードされました[/bold green]")
        console.print(f"保存先: {save_path}")
        console.print(f"サイズ: {len(file_data)} bytes")
        
    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def delete_file(
    file_name: str = typer.Argument(..., help="削除するファイル名"),
    folder_path: str = typer.Option("", "--folder", "-f", help="ファイルが保存されているフォルダパス"),
    force: bool = typer.Option(False, "--force", help="確認なしで削除"),
):
    """SharePointサイトからファイルを削除する"""
    console.print("[bold yellow]SharePointサイトからファイルを削除します[/bold yellow]")
    
    try:
        console.print(f"ファイル名: {file_name}")
        console.print(f"フォルダパス: {folder_path}")
        
        # 確認
        if not force:
            confirm = typer.confirm(f"ファイル '{file_name}' を削除してもよろしいですか？")
            if not confirm:
                console.print("削除がキャンセルされました")
                return
        
        # ファイルを削除
        msgraphs_sites_repo.delete_file(file_name, folder_path)
        
        console.print("✅ [bold green]ファイルが正常に削除されました[/bold green]")
        
    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def delete_files(
    file_names: list[str] = typer.Argument(..., help="削除するファイル名（複数指定可能）"),
    folder_path: str = typer.Option("", "--folder", "-f", help="ファイルが保存されているフォルダパス"),
    force: bool = typer.Option(False, "--force", help="確認なしで削除"),
):
    """SharePointサイトから複数のファイルを同時に削除する"""
    console.print("[bold yellow]SharePointサイトから複数のファイルを削除します[/bold yellow]")
    
    try:
        console.print(f"削除対象: {len(file_names)} 個のファイル")
        console.print(f"フォルダパス: {folder_path}")
        
        # 確認
        if not force:
            confirm = typer.confirm(f"{len(file_names)} 個のファイルを削除してもよろしいですか？")
            if not confirm:
                console.print("削除がキャンセルされました")
                return
        
        # 複数ファイルを削除
        deleted_files = msgraphs_sites_repo.delete_files(file_names, folder_path)
        
        console.print(f"✅ [bold green]{len(deleted_files)} 個のファイルが正常に削除されました[/bold green]")
        
        # 結果を表示
        for file_name in deleted_files:
            console.print(f"削除済み: {file_name}")
        
    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def get_file_info(
    file_name: str = typer.Argument(..., help="情報を取得するファイル名"),
    folder_path: str = typer.Option("", "--folder", "-f", help="ファイルが保存されているフォルダパス"),
    output_format: str = typer.Option("table", "--format", "-o", help="出力形式 (table/json)"),
):
    """SharePointサイトのファイル情報を取得する"""
    console.print("[bold green]SharePointサイトのファイル情報を取得します[/bold green]")
    
    try:
        console.print(f"ファイル名: {file_name}")
        console.print(f"フォルダパス: {folder_path}")
        
        # ファイル情報を取得
        file_info = msgraphs_sites_repo.get_file_info(file_name, folder_path)
        
        if output_format == "json":
            # JSON形式で出力
            file_json = {
                "name": file_info.name,
                "size": file_info.size,
                "content_type": file_info.content_type,
                "last_modified": file_info.last_modified.isoformat() if file_info.last_modified else None,
                "url": file_info.url,
            }
            console.print(json.dumps(file_json, indent=2, ensure_ascii=False))
        else:
            # テーブル形式で出力
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("プロパティ", style="cyan")
            table.add_column("値", style="yellow")
            
            table.add_row("ファイル名", file_info.name)
            table.add_row("サイズ", str(file_info.size) if file_info.size else "N/A")
            table.add_row("コンテンツタイプ", file_info.content_type or "N/A")
            table.add_row("最終更新日", file_info.last_modified.strftime("%Y-%m-%d %H:%M:%S") if file_info.last_modified else "N/A")
            table.add_row("URL", file_info.url or "N/A")
            
            console.print(table)
        
        console.print("✅ [bold green]ファイル情報を取得しました[/bold green]")
        
    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


if __name__ == "__main__":
    app()