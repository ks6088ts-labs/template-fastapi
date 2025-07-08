import io

from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from fastapi.responses import StreamingResponse

from template_fastapi.models.file import File as FileModel
from template_fastapi.repositories.msgraphs_sites import MicrosoftGraphSitesRepository

router = APIRouter()
msgraphs_sites_repo = MicrosoftGraphSitesRepository()


@router.get(
    "/msgraphs/sites/files/",
    response_model=list[FileModel],
    tags=["msgraphs/sites"],
    operation_id="list_sharepoint_files",
)
async def list_sharepoint_files(folder_path: str = Query("", description="フォルダパス")) -> list[FileModel]:
    """
    SharePointサイトのファイル一覧を取得する
    """
    try:
        return msgraphs_sites_repo.list_files(folder_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル一覧の取得に失敗しました: {str(e)}")


@router.post(
    "/msgraphs/sites/files/upload",
    response_model=FileModel,
    tags=["msgraphs/sites"],
    operation_id="upload_sharepoint_file",
)
async def upload_sharepoint_file(
    file: UploadFile = File(...),
    folder_path: str = Query("", description="アップロード先フォルダパス"),
) -> FileModel:
    """
    SharePointサイトに単一のファイルをアップロードする
    """
    try:
        file_data = await file.read()
        return msgraphs_sites_repo.upload_file(file.filename, file_data, folder_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルのアップロードに失敗しました: {str(e)}")


@router.post(
    "/msgraphs/sites/files/upload-multiple",
    response_model=list[FileModel],
    tags=["msgraphs/sites"],
    operation_id="upload_multiple_sharepoint_files",
)
async def upload_multiple_sharepoint_files(
    files: list[UploadFile] = File(...),
    folder_path: str = Query("", description="アップロード先フォルダパス"),
) -> list[FileModel]:
    """
    SharePointサイトに複数のファイルを同時にアップロードする
    """
    try:
        file_data_list = []
        for file in files:
            file_data = await file.read()
            file_data_list.append((file.filename, file_data, file.content_type))

        return msgraphs_sites_repo.upload_files(file_data_list, folder_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"複数ファイルのアップロードに失敗しました: {str(e)}")


@router.get(
    "/msgraphs/sites/files/{file_name}",
    tags=["msgraphs/sites"],
    operation_id="download_sharepoint_file",
)
async def download_sharepoint_file(
    file_name: str,
    folder_path: str = Query("", description="ファイルが保存されているフォルダパス"),
):
    """
    SharePointサイトからファイルをダウンロードする
    """
    try:
        file_data = msgraphs_sites_repo.download_file(file_name, folder_path)
        file_info = msgraphs_sites_repo.get_file_info(file_name, folder_path)

        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=file_info.content_type or "application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
    except Exception as e:
        if "見つかりません" in str(e):
            raise HTTPException(status_code=404, detail=f"ファイル '{file_name}' が見つかりません")
        raise HTTPException(status_code=500, detail=f"ファイルのダウンロードに失敗しました: {str(e)}")


@router.get(
    "/msgraphs/sites/files/{file_name}/info",
    response_model=FileModel,
    tags=["msgraphs/sites"],
    operation_id="get_sharepoint_file_info",
)
async def get_sharepoint_file_info(
    file_name: str,
    folder_path: str = Query("", description="ファイルが保存されているフォルダパス"),
) -> FileModel:
    """
    SharePointサイトのファイル情報を取得する
    """
    try:
        return msgraphs_sites_repo.get_file_info(file_name, folder_path)
    except Exception as e:
        if "見つかりません" in str(e):
            raise HTTPException(status_code=404, detail=f"ファイル '{file_name}' が見つかりません")
        raise HTTPException(status_code=500, detail=f"ファイル情報の取得に失敗しました: {str(e)}")


@router.delete(
    "/msgraphs/sites/files/{file_name}",
    tags=["msgraphs/sites"],
    operation_id="delete_sharepoint_file",
)
async def delete_sharepoint_file(
    file_name: str,
    folder_path: str = Query("", description="ファイルが保存されているフォルダパス"),
) -> dict:
    """
    SharePointサイトのファイルを削除する
    """
    try:
        msgraphs_sites_repo.delete_file(file_name, folder_path)
        return {"message": f"ファイル '{file_name}' を正常に削除しました"}
    except Exception as e:
        if "見つかりません" in str(e):
            raise HTTPException(status_code=404, detail=f"ファイル '{file_name}' が見つかりません")
        raise HTTPException(status_code=500, detail=f"ファイルの削除に失敗しました: {str(e)}")


@router.delete(
    "/msgraphs/sites/files/",
    tags=["msgraphs/sites"],
    operation_id="delete_multiple_sharepoint_files",
)
async def delete_multiple_sharepoint_files(
    file_names: list[str],
    folder_path: str = Query("", description="ファイルが保存されているフォルダパス"),
) -> dict:
    """
    SharePointサイトの複数のファイルを同時に削除する
    """
    try:
        deleted_files = msgraphs_sites_repo.delete_files(file_names, folder_path)
        return {"message": f"{len(deleted_files)} 個のファイルを正常に削除しました", "deleted_files": deleted_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"複数ファイルの削除に失敗しました: {str(e)}")