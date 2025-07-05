from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContainerClient

from template_fastapi.models.file import File
from template_fastapi.settings.azure_blob_storage import get_azure_blob_storage_settings

# 設定の取得
azure_blob_storage_settings = get_azure_blob_storage_settings()


class FileRepository:
    """ファイルデータを管理するリポジトリクラス"""

    def __init__(self):
        self._blob_service_client = None
        self._container_client = None

    @property
    def blob_service_client(self) -> BlobServiceClient:
        """BlobServiceClientを遅延初期化するプロパティ"""
        if self._blob_service_client is None:
            self._blob_service_client = BlobServiceClient.from_connection_string(
                azure_blob_storage_settings.azure_blob_storage_connection_string
            )
        return self._blob_service_client

    @property
    def container_client(self) -> ContainerClient:
        """ContainerClientを遅延初期化するプロパティ"""
        if self._container_client is None:
            self._container_client = self.blob_service_client.get_container_client(
                azure_blob_storage_settings.azure_blob_storage_container_name
            )
        return self._container_client

    def list_files(self, prefix: str | None = None) -> list[File]:
        """ファイル一覧を取得する"""
        try:
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            files = []
            for blob in blobs:
                file_info = File(
                    name=blob.name,
                    size=blob.size,
                    content_type=blob.content_settings.content_type if blob.content_settings else None,
                    last_modified=blob.last_modified,
                )
                files.append(file_info)
            return files
        except Exception as e:
            raise Exception(f"ファイル一覧の取得に失敗しました: {str(e)}")

    def upload_file(self, file_name: str, file_data: bytes, content_type: str | None = None) -> File:
        """ファイルをアップロードする"""
        try:
            blob_client = self.container_client.get_blob_client(file_name)
            blob_client.upload_blob(
                data=file_data,
                overwrite=True,
            )

            # アップロードされたファイル情報を取得
            blob_properties = blob_client.get_blob_properties()
            return File(
                name=blob_properties.name,
                size=blob_properties.size,
                content_type=blob_properties.content_settings.content_type
                if blob_properties.content_settings
                else None,
                last_modified=blob_properties.last_modified,
                url=blob_client.url,
            )
        except Exception as e:
            raise Exception(f"ファイルのアップロードに失敗しました: {str(e)}")

    def upload_files(self, files: list[tuple[str, bytes, str | None]]) -> list[File]:
        """複数のファイルを同時にアップロードする"""
        uploaded_files = []
        for file_name, file_data, content_type in files:
            uploaded_file = self.upload_file(file_name, file_data, content_type)
            uploaded_files.append(uploaded_file)
        return uploaded_files

    def download_file(self, file_name: str) -> bytes:
        """ファイルをダウンロードする"""
        try:
            blob_client = self.container_client.get_blob_client(file_name)
            return blob_client.download_blob().readall()
        except ResourceNotFoundError:
            raise Exception(f"ファイル '{file_name}' が見つかりません")
        except Exception as e:
            raise Exception(f"ファイルのダウンロードに失敗しました: {str(e)}")

    def get_file_info(self, file_name: str) -> File:
        """ファイル情報を取得する"""
        try:
            blob_client = self.container_client.get_blob_client(file_name)
            blob_properties = blob_client.get_blob_properties()
            return File(
                name=blob_properties.name,
                size=blob_properties.size,
                content_type=blob_properties.content_settings.content_type
                if blob_properties.content_settings
                else None,
                last_modified=blob_properties.last_modified,
                url=blob_client.url,
            )
        except ResourceNotFoundError:
            raise Exception(f"ファイル '{file_name}' が見つかりません")
        except Exception as e:
            raise Exception(f"ファイル情報の取得に失敗しました: {str(e)}")

    def delete_file(self, file_name: str) -> bool:
        """ファイルを削除する"""
        try:
            blob_client = self.container_client.get_blob_client(file_name)
            blob_client.delete_blob()
            return True
        except ResourceNotFoundError:
            raise Exception(f"ファイル '{file_name}' が見つかりません")
        except Exception as e:
            raise Exception(f"ファイルの削除に失敗しました: {str(e)}")

    def delete_files(self, file_names: list[str]) -> list[str]:
        """複数のファイルを同時に削除する"""
        deleted_files = []
        for file_name in file_names:
            if self.delete_file(file_name):
                deleted_files.append(file_name)
        return deleted_files
