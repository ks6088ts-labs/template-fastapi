#!/usr/bin/env python
# filepath: /home/runner/work/template-fastapi/template-fastapi/scripts/speeches.py

import json
import time

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from template_fastapi.models.speech import BatchTranscriptionRequest, TranscriptionStatus
from template_fastapi.repositories.speeches import SpeechRepository

app = typer.Typer()
console = Console()
speech_repo = SpeechRepository()


@app.command()
def create_transcription(
    content_urls: list[str] = typer.Argument(..., help="転写するファイルのURL（複数指定可能）"),
    locale: str = typer.Option("ja-JP", "--locale", "-l", help="言語設定"),
    display_name: str = typer.Option(None, "--name", "-n", help="転写ジョブの表示名"),
):
    """新しい転写ジョブを作成する"""
    console.print("[bold green]転写ジョブを作成します[/bold green]")
    console.print(f"ファイルURL: {', '.join(content_urls)}")
    console.print(f"言語設定: {locale}")

    try:
        request = BatchTranscriptionRequest(
            content_urls=content_urls,
            locale=locale,
            display_name=display_name or "CLI Batch Transcription",
        )

        response = speech_repo.create_transcription_job(request)

        console.print("✅ [bold green]転写ジョブが正常に作成されました[/bold green]")
        console.print(f"ジョブID: {response.job_id}")
        console.print(f"ステータス: {response.status.value}")

        if response.message:
            console.print(f"メッセージ: {response.message}")

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def get_transcription(
    job_id: str = typer.Argument(..., help="転写ジョブID"),
):
    """転写ジョブの状態を取得する"""
    console.print("[bold green]転写ジョブの状態を取得します[/bold green]")
    console.print(f"ジョブID: {job_id}")

    try:
        job = speech_repo.get_transcription_job(job_id)

        console.print("\n[bold blue]転写ジョブ情報[/bold blue]:")
        console.print(f"ID: {job.id}")
        console.print(f"名前: {job.name}")
        console.print(f"ステータス: {job.status.value}")
        console.print(f"作成日時: {job.created_date_time}")
        console.print(f"最終更新日時: {job.last_action_date_time}")

        if job.links:
            console.print(f"リンク: {json.dumps(job.links, indent=2, ensure_ascii=False)}")

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def get_transcription_files(
    job_id: str = typer.Argument(..., help="転写ジョブID"),
):
    """転写ジョブのファイル一覧を取得する"""
    console.print("[bold green]転写ファイル一覧を取得します[/bold green]")
    console.print(f"ジョブID: {job_id}")

    try:
        files = speech_repo.get_transcription_files(job_id)

        if not files:
            console.print("[yellow]転写ファイルが見つかりませんでした[/yellow]")
            return

        # テーブルで表示
        table = Table(title="転写ファイル一覧")
        table.add_column("名前", style="cyan")
        table.add_column("種類", style="green")
        table.add_column("リンク", style="yellow")
        for file in files:
            print(file)

        for file in files:
            table.add_row(
                file.get("name", "N/A"), file.get("kind", "N/A"), file.get("links", {}).get("contentUrl", "N/A")
            )

        console.print(table)
        console.print(f"[bold blue]合計: {len(files)}件[/bold blue]")

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def get_transcription_result(
    file_url: str = typer.Argument(..., help="転写結果ファイルのURL"),
    save_file: str = typer.Option(None, "--save", "-s", help="結果を保存するファイル名"),
):
    """転写結果を取得する"""
    console.print("[bold green]転写結果を取得します[/bold green]")
    console.print(f"ファイルURL: {file_url}")

    try:
        result = speech_repo.get_transcription_result(file_url)

        console.print("\n[bold blue]転写結果[/bold blue]:")
        console.print(f"ソース: {result.source}")
        console.print(f"タイムスタンプ: {result.timestamp}")
        console.print(f"継続時間: {result.duration_in_ticks}")

        if result.combined_recognized_phrases:
            console.print("\n[bold yellow]統合認識フレーズ[/bold yellow]:")
            for phrase in result.combined_recognized_phrases:
                console.print(f"- {phrase.get('display', 'N/A')}")

        if result.recognized_phrases:
            console.print(f"\n[bold yellow]認識フレーズ（{len(result.recognized_phrases)}件）[/bold yellow]:")
            for i, phrase in enumerate(result.recognized_phrases[:5]):  # 最初の5件のみ表示
                console.print(f"{i + 1}. {phrase.get('display', 'N/A')}")

            if len(result.recognized_phrases) > 5:
                console.print(f"... および {len(result.recognized_phrases) - 5} 件の追加フレーズ")

        # ファイルに保存
        if save_file:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(result.model_dump(), f, ensure_ascii=False, indent=2, default=str)
            console.print(f"✅ 結果を {save_file} に保存しました")

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def delete_transcription(
    job_id: str = typer.Argument(..., help="転写ジョブID"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除"),
):
    """転写ジョブを削除する"""
    console.print("[bold yellow]転写ジョブを削除します[/bold yellow]")
    console.print(f"ジョブID: {job_id}")

    if not force:
        confirm = typer.confirm("本当に削除しますか？")
        if not confirm:
            console.print("削除をキャンセルしました")
            return

    try:
        success = speech_repo.delete_transcription_job(job_id)

        if success:
            console.print(f"✅ [bold green]転写ジョブ '{job_id}' を正常に削除しました[/bold green]")
        else:
            console.print("❌ [bold red]転写ジョブの削除に失敗しました[/bold red]")

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def list_transcriptions():
    """転写ジョブの一覧を取得する"""
    console.print("[bold green]転写ジョブ一覧を取得します[/bold green]")

    try:
        jobs = speech_repo.list_transcription_jobs()

        if not jobs:
            console.print("[yellow]転写ジョブが見つかりませんでした[/yellow]")
            return

        # テーブルで表示
        table = Table(title="転写ジョブ一覧")
        table.add_column("ID", style="cyan")
        table.add_column("名前", style="green")
        table.add_column("ステータス", style="yellow")
        table.add_column("作成日時", style="magenta")
        table.add_column("最終更新日時", style="blue")

        for job in jobs:
            table.add_row(
                job.id,
                job.name or "N/A",
                job.status.value,
                str(job.created_date_time) if job.created_date_time else "N/A",
                str(job.last_action_date_time) if job.last_action_date_time else "N/A",
            )

        console.print(table)
        console.print(f"[bold blue]合計: {len(jobs)}件[/bold blue]")

    except Exception as e:
        console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")


@app.command()
def wait_for_completion(
    job_id: str = typer.Argument(..., help="転写ジョブID"),
    timeout: int = typer.Option(300, "--timeout", "-t", help="タイムアウト時間（秒）"),
    interval: int = typer.Option(10, "--interval", "-i", help="チェック間隔（秒）"),
):
    """転写ジョブの完了を待つ"""
    console.print("[bold green]転写ジョブの完了を待ちます[/bold green]")
    console.print(f"ジョブID: {job_id}")
    console.print(f"タイムアウト: {timeout}秒")
    console.print(f"チェック間隔: {interval}秒")

    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="転写処理中...", total=None)

        while time.time() - start_time < timeout:
            try:
                job = speech_repo.get_transcription_job(job_id)

                if job.status == TranscriptionStatus.SUCCEEDED:
                    progress.update(task, description="✅ 転写が完了しました")
                    console.print("✅ [bold green]転写ジョブが正常に完了しました[/bold green]")
                    console.print(f"ジョブID: {job.id}")
                    console.print(f"最終更新日時: {job.last_action_date_time}")
                    return
                elif job.status == TranscriptionStatus.FAILED:
                    progress.update(task, description="❌ 転写が失敗しました")
                    console.print("❌ [bold red]転写ジョブが失敗しました[/bold red]")
                    console.print(f"ジョブID: {job.id}")
                    return
                elif job.status == TranscriptionStatus.RUNNING:
                    progress.update(task, description="🔄 転写処理中...")
                else:
                    progress.update(task, description=f"⏳ 待機中 ({job.status.value})")

                time.sleep(interval)

            except Exception as e:
                progress.update(task, description=f"❌ エラー: {str(e)}")
                console.print(f"❌ [bold red]エラー[/bold red]: {str(e)}")
                return

        # タイムアウト
        console.print(f"⏰ [bold yellow]タイムアウトしました（{timeout}秒）[/bold yellow]")
        console.print("転写ジョブはまだ処理中の可能性があります")


if __name__ == "__main__":
    app()
