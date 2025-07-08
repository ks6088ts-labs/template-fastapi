from datetime import datetime
from io import BytesIO

from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.upload_session import UploadSession

from template_fastapi.models.file import File
from template_fastapi.settings.microsoft_graph import get_microsoft_graph_settings

# 設定の取得
microsoft_graph_settings = get_microsoft_graph_settings()


class MicrosoftGraphSitesRepository:
    """Microsoft Graph Sites（SharePoint）のファイルを管理するリポジトリクラス"""

    def __init__(self):
        self._graph_client = None

    @property
    def graph_client(self) -> GraphServiceClient:
        """GraphServiceClientを遅延初期化するプロパティ"""
        if self._graph_client is None:
            credential = ClientSecretCredential(
                tenant_id=microsoft_graph_settings.microsoft_graph_tenant_id,
                client_id=microsoft_graph_settings.microsoft_graph_client_id,
                client_secret=microsoft_graph_settings.microsoft_graph_client_secret,
            )
            self._graph_client = GraphServiceClient(credentials=credential)
        return self._graph_client

    def list_files(self, folder_path: str = "") -> list[File]:
        """ファイル一覧を取得する"""
        try:
            if folder_path:
                # フォルダ内のファイルを取得
                drive_items = self.graph_client.sites.by_site_id(
                    microsoft_graph_settings.microsoft_graph_site_id
                ).drive.root.item_with_path(folder_path).children.get()
            else:
                # ルートフォルダのファイルを取得
                drive_items = self.graph_client.sites.by_site_id(
                    microsoft_graph_settings.microsoft_graph_site_id
                ).drive.root.children.get()

            files = []
            if drive_items and drive_items.value:
                for item in drive_items.value:
                    if item.file:  # ファイルのみを対象とする（フォルダは除外）
                        files.append(
                            File(
                                name=item.name,
                                size=item.size,
                                content_type=item.file.mime_type,
                                last_modified=item.last_modified_date_time,
                                url=item.web_url,
                            )
                        )
            return files
        except Exception as e:
            raise Exception(f"ファイル一覧の取得に失敗しました: {str(e)}")

    def upload_file(self, file_name: str, file_data: bytes, folder_path: str = "") -> File:
        """ファイルをアップロードする"""
        try:
            # ファイルパスを構築
            file_path = f"{folder_path}/{file_name}" if folder_path else file_name

            # ファイルをアップロード
            upload_result = self.graph_client.sites.by_site_id(
                microsoft_graph_settings.microsoft_graph_site_id
            ).drive.root.item_with_path(file_path).content.put(file_data)

            # アップロードされたファイル情報を取得
            file_info = self.graph_client.sites.by_site_id(
                microsoft_graph_settings.microsoft_graph_site_id
            ).drive.root.item_with_path(file_path).get()

            return File(
                name=file_info.name,
                size=file_info.size,
                content_type=file_info.file.mime_type if file_info.file else None,
                last_modified=file_info.last_modified_date_time,
                url=file_info.web_url,
            )
        except Exception as e:
            raise Exception(f"ファイルのアップロードに失敗しました: {str(e)}")

    def upload_files(self, files: list[tuple[str, bytes, str]], folder_path: str = "") -> list[File]:
        """複数のファイルを同時にアップロードする"""
        uploaded_files = []
        for file_name, file_data, content_type in files:
            uploaded_file = self.upload_file(file_name, file_data, folder_path)
            uploaded_files.append(uploaded_file)
        return uploaded_files

    def download_file(self, file_name: str, folder_path: str = "") -> bytes:
        """ファイルをダウンロードする"""
        try:
            # ファイルパスを構築
            file_path = f"{folder_path}/{file_name}" if folder_path else file_name

            # ファイルの内容を取得
            content = self.graph_client.sites.by_site_id(
                microsoft_graph_settings.microsoft_graph_site_id
            ).drive.root.item_with_path(file_path).content.get()

            return content
        except Exception as e:
            raise Exception(f"ファイルのダウンロードに失敗しました: {str(e)}")

    def get_file_info(self, file_name: str, folder_path: str = "") -> File:
        """ファイル情報を取得する"""
        try:
            # ファイルパスを構築
            file_path = f"{folder_path}/{file_name}" if folder_path else file_name

            # ファイル情報を取得
            file_info = self.graph_client.sites.by_site_id(
                microsoft_graph_settings.microsoft_graph_site_id
            ).drive.root.item_with_path(file_path).get()

            return File(
                name=file_info.name,
                size=file_info.size,
                content_type=file_info.file.mime_type if file_info.file else None,
                last_modified=file_info.last_modified_date_time,
                url=file_info.web_url,
            )
        except Exception as e:
            raise Exception(f"ファイル情報の取得に失敗しました: {str(e)}")

    def delete_file(self, file_name: str, folder_path: str = "") -> bool:
        """ファイルを削除する"""
        try:
            # ファイルパスを構築
            file_path = f"{folder_path}/{file_name}" if folder_path else file_name

            # ファイルを削除
            self.graph_client.sites.by_site_id(
                microsoft_graph_settings.microsoft_graph_site_id
            ).drive.root.item_with_path(file_path).delete()

            return True
        except Exception as e:
            if "not found" in str(e).lower():
                raise Exception(f"ファイル '{file_name}' が見つかりません")
            raise Exception(f"ファイルの削除に失敗しました: {str(e)}")

    def delete_files(self, file_names: list[str], folder_path: str = "") -> list[str]:
        """複数のファイルを同時に削除する"""
        deleted_files = []
        for file_name in file_names:
            if self.delete_file(file_name, folder_path):
                deleted_files.append(file_name)
        return deleted_files