import json
from typing import Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from template_fastapi.models.speech import (
    BatchTranscriptionRequest,
    BatchTranscriptionResponse,
    TranscriptionContent,
    TranscriptionJob,
    TranscriptionStatus,
)
from template_fastapi.settings.azure_speech import get_azure_speech_settings

# 設定の取得
azure_speech_settings = get_azure_speech_settings()


class SpeechRepository:
    """音声認識データを管理するリポジトリクラス"""

    def __init__(self):
        self.speech_key = azure_speech_settings.azure_ai_speech_api_key
        self.speech_endpoint = azure_speech_settings.azure_ai_speech_endpoint
        self.api_version = "v3.2-preview.2"
        self.base_url = urljoin(self.speech_endpoint, f"speechtotext/{self.api_version}/")

        # セッションの設定
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # ヘッダーの設定
        self.headers = {
            "Ocp-Apim-Subscription-Key": self.speech_key,
            "Content-Type": "application/json",
        }

    def create_transcription_job(self, request: BatchTranscriptionRequest) -> BatchTranscriptionResponse:
        """バッチ転写ジョブを作成する"""
        url = urljoin(self.base_url, "transcriptions")

        # Whisperモデルを使用する場合の設定
        payload = {
            "contentUrls": request.content_urls,
            "locale": request.locale,
            "displayName": request.display_name or "Batch Transcription",
            "model": None,  # Whisperモデルを使用する場合はNone
            "properties": {},
        }

        try:
            response = self.session.post(url, headers=self.headers, data=json.dumps(payload), timeout=30)
            response.raise_for_status()

            result = response.json()
            job_id = result.get("self", "").split("/")[-1]

            return BatchTranscriptionResponse(
                job_id=job_id,
                status=TranscriptionStatus(result.get("status", "NotStarted")),
                message="転写ジョブが正常に作成されました",
            )

        except requests.exceptions.RequestException as e:
            raise Exception(f"転写ジョブの作成に失敗しました: {str(e)}")

    def get_transcription_job(self, job_id: str) -> TranscriptionJob:
        """転写ジョブの状態を取得する"""
        url = urljoin(self.base_url, f"transcriptions/{job_id}")

        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            result = response.json()

            return TranscriptionJob(
                id=job_id,
                name=result.get("displayName"),
                status=TranscriptionStatus(result.get("status", "NotStarted")),
                created_date_time=result.get("createdDateTime"),
                last_action_date_time=result.get("lastActionDateTime"),
                self_url=result.get("self"),
                links=result.get("links", {}),
            )

        except requests.exceptions.RequestException as e:
            raise Exception(f"転写ジョブの取得に失敗しました: {str(e)}")

    def get_transcription_files(self, job_id: str) -> list[dict[str, Any]]:
        """転写ジョブのファイル一覧を取得する"""
        url = urljoin(self.base_url, f"transcriptions/{job_id}/files")

        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result.get("values", [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"転写ファイル一覧の取得に失敗しました: {str(e)}")

    def get_transcription_result(self, file_url: str) -> TranscriptionContent:
        """転写結果を取得する"""
        try:
            response = self.session.get(file_url, headers=self.headers, timeout=30)
            response.raise_for_status()

            result = response.json()

            return TranscriptionContent(
                source=result.get("source"),
                timestamp=result.get("timestamp"),
                duration_in_ticks=result.get("durationInTicks"),
                combined_recognized_phrases=result.get("combinedRecognizedPhrases", []),
                recognized_phrases=result.get("recognizedPhrases", []),
            )

        except requests.exceptions.RequestException as e:
            raise Exception(f"転写結果の取得に失敗しました: {str(e)}")

    def delete_transcription_job(self, job_id: str) -> bool:
        """転写ジョブを削除する"""
        url = urljoin(self.base_url, f"transcriptions/{job_id}")

        try:
            response = self.session.delete(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            raise Exception(f"転写ジョブの削除に失敗しました: {str(e)}")

    def list_transcription_jobs(self) -> list[TranscriptionJob]:
        """転写ジョブの一覧を取得する"""
        url = urljoin(self.base_url, "transcriptions")
        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            jobs = []

            for job_data in result.get("values", []):
                job_id = job_data.get("self", "").split("/")[-1]
                jobs.append(
                    TranscriptionJob(
                        id=job_id,
                        name=job_data.get("displayName"),
                        status=TranscriptionStatus(job_data.get("status", "NotStarted")),
                        created_date_time=job_data.get("createdDateTime"),
                        last_action_date_time=job_data.get("lastActionDateTime"),
                        self_url=job_data.get("self"),
                        links=job_data.get("links", {}),
                    )
                )

            return jobs

        except requests.exceptions.RequestException as e:
            raise Exception(f"転写ジョブ一覧の取得に失敗しました: {str(e)}")
