#!/usr/bin/env python
# filepath: /home/runner/work/template-fastapi/template-fastapi/scripts/files.py

import os
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from template_fastapi.repositories.files import FileRepository

app = typer.Typer()
console = Console()
file_repo = FileRepository()


@app.command()
def list_files(
    prefix: Optional[str] = typer.Option(None, "--prefix", "-p", help="ファイル名のプレフィックス"),
):
    """ファイル一覧を取得する"""
    console.print(f"[bold green]ファイル一覧[/bold green]を取得します")
    
    if prefix:
        console.print(f"プレフィックス: {prefix}")
    
    try:
        files = file_repo.list_files(prefix=prefix)
        
        if not files:
            console.print("[yellow]ファイルが見つかりませんでした[/yellow]")
            return
        
        # テーブルで表示
        table = Table(title="ファイル一覧")
        table.add_column("ファイル名", style="cyan")
        table.add_column("サイズ (bytes)", style="green")
        table.add_column("コンテンツタイプ", style="yellow")
        table.add_column("最終更新日時", style="magenta")
        
        for file in files:
            table.add_row(
                file.name,
                str(file.size) if file.size else "N/A",
                file.content_type or "N/A",
                file.last_modified.strftime("%Y-%m-%d %H:%M:%S") if file.last_modified else "N/A"
            )
        
        console.print(table)
        console.print(f"[bold blue]合計: {len(files)}件[/bold blue]")
    
    except Exception as e:
        console.print(f"[bold red]エラー[/bold red]: {str(e)}")


@app.command()
def upload_file(
    file_path: str = typer.Argument(..., help="アップロードするファイルのパス"),
    blob_name: Optional[str] = typer.Option(None, "--name", "-n", help="Blob名（指定しない場合はファイル名を使用）"),
):
    """単一のファイルをアップロードする"""
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        console.print(f"[bold red]エラー[/bold red]: ファイル '{file_path}' が見つかりません")
        return
    
    if not file_path_obj.is_file():
        console.print(f"[bold red]エラー[/bold red]: '{file_path}' はファイルではありません")
        return
    
    blob_name = blob_name or file_path_obj.name
    console.print(f"[bold green]ファイル[/bold green]: {file_path} -> {blob_name}")
    
    try:
        with open(file_path_obj, "rb") as f:
            file_data = f.read()
        
        uploaded_file = file_repo.upload_file(
            file_name=blob_name,
            file_data=file_data,
            content_type=None  # Let Azure detect the content type
        )
        
        console.print(f"[bold green]アップロード成功[/bold green]")
        console.print(f"  ファイル名: {uploaded_file.name}")
        console.print(f"  サイズ: {uploaded_file.size} bytes")
        console.print(f"  コンテンツタイプ: {uploaded_file.content_type}")
        console.print(f"  URL: {uploaded_file.url}")
    
    except Exception as e:
        console.print(f"[bold red]エラー[/bold red]: {str(e)}")


@app.command()
def upload_multiple_files(
    file_paths: List[str] = typer.Argument(..., help="アップロードするファイルのパス（複数指定可能）"),
):
    """複数のファイルを同時にアップロードする"""
    console.print(f"[bold green]複数ファイル[/bold green]をアップロードします")
    
    # ファイルの存在チェック
    valid_files = []
    for file_path in file_paths:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            console.print(f"[bold red]警告[/bold red]: ファイル '{file_path}' が見つかりません - スキップします")
            continue
        if not file_path_obj.is_file():
            console.print(f"[bold red]警告[/bold red]: '{file_path}' はファイルではありません - スキップします")
            continue
        valid_files.append(file_path_obj)
    
    if not valid_files:
        console.print("[bold red]エラー[/bold red]: 有効なファイルが見つかりませんでした")
        return
    
    try:
        file_data_list = []
        for file_path_obj in valid_files:
            with open(file_path_obj, "rb") as f:
                file_data = f.read()
            file_data_list.append((file_path_obj.name, file_data, None))
        
        uploaded_files = file_repo.upload_files(file_data_list)
        
        console.print(f"[bold green]アップロード成功[/bold green]: {len(uploaded_files)}件")
        for uploaded_file in uploaded_files:
            console.print(f"  - {uploaded_file.name} ({uploaded_file.size} bytes)")
    
    except Exception as e:
        console.print(f"[bold red]エラー[/bold red]: {str(e)}")


@app.command()
def download_file(
    blob_name: str = typer.Argument(..., help="ダウンロードするBlobの名前"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="出力ファイルのパス"),
):
    """ファイルをダウンロードする"""
    console.print(f"[bold green]ファイル[/bold green]: {blob_name} をダウンロードします")
    
    try:
        file_data = file_repo.download_file(blob_name)
        
        output_path = output_path or blob_name
        output_path_obj = Path(output_path)
        
        with open(output_path_obj, "wb") as f:
            f.write(file_data)
        
        console.print(f"[bold green]ダウンロード成功[/bold green]")
        console.print(f"  出力先: {output_path_obj.absolute()}")
        console.print(f"  サイズ: {len(file_data)} bytes")
    
    except Exception as e:
        console.print(f"[bold red]エラー[/bold red]: {str(e)}")


@app.command()
def get_file_info(
    blob_name: str = typer.Argument(..., help="情報を取得するBlobの名前"),
):
    """ファイル情報を取得する"""
    console.print(f"[bold green]ファイル情報[/bold green]: {blob_name}")
    
    try:
        file_info = file_repo.get_file_info(blob_name)
        
        console.print(f"  ファイル名: {file_info.name}")
        console.print(f"  サイズ: {file_info.size} bytes")
        console.print(f"  コンテンツタイプ: {file_info.content_type}")
        console.print(f"  最終更新日時: {file_info.last_modified}")
        console.print(f"  URL: {file_info.url}")
    
    except Exception as e:
        console.print(f"[bold red]エラー[/bold red]: {str(e)}")


@app.command()
def delete_file(
    blob_name: str = typer.Argument(..., help="削除するBlobの名前"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除する"),
):
    """ファイルを削除する"""
    console.print(f"[bold green]ファイル削除[/bold green]: {blob_name}")
    
    try:
        # 削除前に確認
        if not force:
            file_info = file_repo.get_file_info(blob_name)
            console.print("以下のファイルを削除しようとしています：")
            console.print(f"  ファイル名: {file_info.name}")
            console.print(f"  サイズ: {file_info.size} bytes")
            console.print(f"  最終更新日時: {file_info.last_modified}")
            
            if not typer.confirm("削除してもよろしいですか？"):
                console.print("[yellow]削除をキャンセルしました[/yellow]")
                return
        
        file_repo.delete_file(blob_name)
        console.print(f"[bold green]削除成功[/bold green]: {blob_name}")
    
    except Exception as e:
        console.print(f"[bold red]エラー[/bold red]: {str(e)}")


@app.command()
def delete_multiple_files(
    blob_names: List[str] = typer.Argument(..., help="削除するBlobの名前（複数指定可能）"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除する"),
):
    """複数のファイルを同時に削除する"""
    console.print(f"[bold green]複数ファイル削除[/bold green]: {len(blob_names)}件")
    
    try:
        # 削除前に確認
        if not force:
            console.print("以下のファイルを削除しようとしています：")
            for blob_name in blob_names:
                console.print(f"  - {blob_name}")
            
            if not typer.confirm("削除してもよろしいですか？"):
                console.print("[yellow]削除をキャンセルしました[/yellow]")
                return
        
        deleted_files = file_repo.delete_files(blob_names)
        console.print(f"[bold green]削除成功[/bold green]: {len(deleted_files)}件")
        for deleted_file in deleted_files:
            console.print(f"  - {deleted_file}")
    
    except Exception as e:
        console.print(f"[bold red]エラー[/bold red]: {str(e)}")


if __name__ == "__main__":
    app()