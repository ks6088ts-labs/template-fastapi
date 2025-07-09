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

    def __init__(self, graph_client: GraphServiceClient):
        self.graph_client = graph_client

    def list_files(self, site_id: str, folder_path: str = "") -> list[File]:
        """SharePointサイトのファイル一覧を取得する"""
        try:
            if folder_path:
                # フォルダ内のファイルを取得
                drive_items = self.graph_client.sites.by_site_id(site_id).drive.root.item_with_path(folder_path).children.get()
            else:
                # ルートディレクトリのファイルを取得
                drive_items = self.graph_client.sites.by_site_id(site_id).drive.root.children.get()

            files = []
            if drive_items and drive_items.value:
                for item in drive_items.value:
                    if item.file:  # ファイルのみ（フォルダは除外）
                        file_obj = File(
                            name=item.name,
                            size=item.size or 0,
                            content_type=item.file.mime_type if item.file else "application/octet-stream",
                            created_at=item.created_date_time.replace(tzinfo=None) if item.created_date_time else datetime.now(),
                            updated_at=item.last_modified_date_time.replace(tzinfo=None) if item.last_modified_date_time else datetime.now(),
                        )
                        files.append(file_obj)
            return files
        except Exception as e:
            raise RuntimeError(f"ファイル一覧の取得に失敗しました: {str(e)}")

    def upload_file(self, site_id: str, file_content: bytes, file_name: str, folder_path: str = "") -> File:
        """SharePointサイトにファイルをアップロードする"""
        try:
            # アップロード先のパスを構築
            upload_path = f"{folder_path}/{file_name}" if folder_path else file_name

            # ファイルをアップロード
            uploaded_item = self.graph_client.sites.by_site_id(site_id).drive.root.item_with_path(upload_path).content.put(
                file_content,
                content_type="application/octet-stream"
            )

            # アップロードされたファイルの情報を取得
            return File(
                name=uploaded_item.name,
                size=uploaded_item.size or len(file_content),
                content_type=uploaded_item.file.mime_type if uploaded_item.file else "application/octet-stream",
                created_at=uploaded_item.created_date_time.replace(tzinfo=None) if uploaded_item.created_date_time else datetime.now(),
                updated_at=uploaded_item.last_modified_date_time.replace(tzinfo=None) if uploaded_item.last_modified_date_time else datetime.now(),
            )
        except Exception as e:
            raise RuntimeError(f"ファイルのアップロードに失敗しました: {str(e)}")

    def upload_multiple_files(self, site_id: str, files_data: list[tuple[bytes, str]], folder_path: str = "") -> list[File]:
        """SharePointサイトに複数のファイルを同時にアップロードする"""
        uploaded_files = []
        for file_content, file_name in files_data:
            uploaded_file = self.upload_file(site_id, file_content, file_name, folder_path)
            uploaded_files.append(uploaded_file)
        return uploaded_files

    def download_file(self, site_id: str, file_name: str, folder_path: str = "") -> bytes:
        """SharePointサイトからファイルをダウンロードする"""
        try:
            # ファイルパスを構築
            file_path = f"{folder_path}/{file_name}" if folder_path else file_name

            # ファイルの内容を取得
            content = self.graph_client.sites.by_site_id(site_id).drive.root.item_with_path(file_path).content.get()
            return content
        except Exception as e:
            raise RuntimeError(f"ファイルのダウンロードに失敗しました: {str(e)}")

    def delete_file(self, site_id: str, file_name: str, folder_path: str = "") -> bool:
        """SharePointサイトからファイルを削除する"""
        try:
            # ファイルパスを構築
            file_path = f"{folder_path}/{file_name}" if folder_path else file_name

            # ファイルを削除
            self.graph_client.sites.by_site_id(site_id).drive.root.item_with_path(file_path).delete()
            return True
        except Exception as e:
            raise RuntimeError(f"ファイルの削除に失敗しました: {str(e)}")

    def delete_multiple_files(self, site_id: str, file_names: list[str], folder_path: str = "") -> list[str]:
        """SharePointサイトから複数のファイルを削除する"""
        deleted_files = []
        for file_name in file_names:
            try:
                if self.delete_file(site_id, file_name, folder_path):
                    deleted_files.append(file_name)
            except Exception as e:
                print(f"ファイル {file_name} の削除に失敗しました: {str(e)}")
        return deleted_files

    def get_file_info(self, site_id: str, file_name: str, folder_path: str = "") -> File:
        """SharePointサイトのファイル情報を取得する"""
        try:
            # ファイルパスを構築
            file_path = f"{folder_path}/{file_name}" if folder_path else file_name

            # ファイル情報を取得
            item = self.graph_client.sites.by_site_id(site_id).drive.root.item_with_path(file_path).get()

            return File(
                name=item.name,
                size=item.size or 0,
                content_type=item.file.mime_type if item.file else "application/octet-stream",
                created_at=item.created_date_time.replace(tzinfo=None) if item.created_date_time else datetime.now(),
                updated_at=item.last_modified_date_time.replace(tzinfo=None) if item.last_modified_date_time else datetime.now(),
            )
        except Exception as e:
            raise RuntimeError(f"ファイル情報の取得に失敗しました: {str(e)}")


class MicrosoftGraphRepository:
    """Microsoft Graphの各種サービスを統合するリポジトリクラス"""

    def __init__(self):
        self._graph_client = None
        self._sites = None

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

    @property
    def sites(self) -> MicrosoftGraphSitesRepository:
        """Sitesサブモジュールのプロパティ"""
        if self._sites is None:
            self._sites = MicrosoftGraphSitesRepository(self.graph_client)
        return self._sites