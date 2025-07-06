from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class TranscriptionStatus(str, Enum):
    """転写処理のステータス"""

    NOT_STARTED = "NotStarted"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"


class TranscriptionJob(BaseModel):
    """転写ジョブの情報を表すモデル"""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str | None = None
    status: TranscriptionStatus
    created_date_time: datetime | None = None
    last_action_date_time: datetime | None = None
    self_url: str | None = None
    links: dict[str, str] | None = None


class TranscriptionResult(BaseModel):
    """転写結果を表すモデル"""

    model_config = ConfigDict(extra="ignore")

    source: str | None = None
    duration: str | None = None
    text: str | None = None
    confidence: float | None = None
    speaker: int | None = None
    offset: str | None = None


class TranscriptionContent(BaseModel):
    """転写内容全体を表すモデル"""

    model_config = ConfigDict(extra="ignore")

    source: str | None = None
    timestamp: datetime | None = None
    duration_in_ticks: int | None = None
    combined_recognized_phrases: list[dict[str, Any]] | None = None
    recognized_phrases: list[dict[str, Any]] | None = None


class BatchTranscriptionRequest(BaseModel):
    """バッチ転写リクエストを表すモデル"""

    model_config = ConfigDict(extra="ignore")

    content_urls: list[str] = [
        "https://<storage_account_name>.blob.core.windows.net/<container_name>/<file1.m4a>?<sas_token>",
        "https://<storage_account_name>.blob.core.windows.net/<container_name>/<file2.m4a>?<sas_token>",
    ]
    locale: str = "ja-JP"
    display_name: str | None = "My Batch Transcription"


class BatchTranscriptionResponse(BaseModel):
    """バッチ転写レスポンスを表すモデル"""

    model_config = ConfigDict(extra="ignore")

    job_id: str
    status: TranscriptionStatus
    message: str | None = None
