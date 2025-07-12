from typing import Any

from fastapi import APIRouter, HTTPException, Query

from template_fastapi.models.speech import (
    BatchTranscriptionRequest,
    BatchTranscriptionResponse,
    TranscriptionContent,
    TranscriptionJob,
)
from template_fastapi.repositories.speeches import SpeechRepository

router = APIRouter()
speech_repo = SpeechRepository()


@router.post(
    "/transcriptions/",
    response_model=BatchTranscriptionResponse,
    operation_id="create_transcription_job",
)
async def create_transcription_job(request: BatchTranscriptionRequest) -> BatchTranscriptionResponse:
    """
    バッチ転写ジョブを作成する
    """
    try:
        return speech_repo.create_transcription_job(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"転写ジョブの作成に失敗しました: {str(e)}")


@router.get(
    "/transcriptions/{job_id}",
    response_model=TranscriptionJob,
    operation_id="get_transcription_job",
)
async def get_transcription_job(job_id: str) -> TranscriptionJob:
    """
    転写ジョブの状態を取得する
    """
    try:
        return speech_repo.get_transcription_job(job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"転写ジョブの取得に失敗しました: {str(e)}")


@router.get(
    "/transcriptions/{job_id}/files",
    response_model=list[dict[str, Any]],
    operation_id="get_transcription_files",
)
async def get_transcription_files(job_id: str) -> list[dict[str, Any]]:
    """
    転写ジョブのファイル一覧を取得する
    """
    try:
        return speech_repo.get_transcription_files(job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"転写ファイル一覧の取得に失敗しました: {str(e)}")


@router.get(
    "/transcriptions/{job_id}/result",
    response_model=TranscriptionContent,
    operation_id="get_transcription_result",
)
async def get_transcription_result(
    job_id: str, file_url: str = Query(..., description="転写結果ファイルのURL")
) -> TranscriptionContent:
    """
    転写結果を取得する
    """
    try:
        return speech_repo.get_transcription_result(file_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"転写結果の取得に失敗しました: {str(e)}")


@router.delete(
    "/transcriptions/{job_id}",
    operation_id="delete_transcription_job",
)
async def delete_transcription_job(job_id: str) -> dict:
    """
    転写ジョブを削除する
    """
    try:
        success = speech_repo.delete_transcription_job(job_id)
        if success:
            return {"message": f"転写ジョブ '{job_id}' を正常に削除しました"}
        else:
            raise HTTPException(status_code=500, detail="転写ジョブの削除に失敗しました")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"転写ジョブの削除に失敗しました: {str(e)}")


@router.get(
    "/transcriptions/",
    response_model=list[TranscriptionJob],
    operation_id="list_transcription_jobs",
)
async def list_transcription_jobs() -> list[TranscriptionJob]:
    """
    転写ジョブの一覧を取得する
    """
    try:
        return speech_repo.list_transcription_jobs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"転写ジョブ一覧の取得に失敗しました: {str(e)}")
