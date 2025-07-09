import io

from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from fastapi.responses import StreamingResponse

from template_fastapi.models.file import File as FileModel
from template_fastapi.repositories.msgraphs import MicrosoftGraphRepository

router = APIRouter()
msgraphs_repo = MicrosoftGraphRepository()


@router.get(
    "/files/",
    response_model=list[FileModel],
    operation_id="list_sharepoint_files",
)
async def list_sharepoint_files(
    site_id: str = Query(..., description="SharePoint Site ID"),
    folder_path: str = Query("", description="フォルダパス")
) -> list[FileModel]:
    """
    SharePointサイトのファイル一覧を取得する
    """
    try:
        return msgraphs_repo.sites.list_files(site_id, folder_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル一覧の取得に失敗しました: {str(e)}")


@router.post(
    "/files/upload",
    response_model=FileModel,
    operation_id="upload_sharepoint_file",
)
async def upload_sharepoint_file(
    site_id: str = Query(..., description="SharePoint Site ID"),
    file: UploadFile = File(...),
    folder_path: str = Query("", description="アップロード先のフォルダパス")
) -> FileModel:
    """
    SharePointサイトにファイルをアップロードする
    """
    try:
        file_content = await file.read()
        return msgraphs_repo.sites.upload_file(site_id, file_content, file.filename or "unknown", folder_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルのアップロードに失敗しました: {str(e)}")


@router.post(
    "/files/upload-multiple",
    response_model=list[FileModel],
    operation_id="upload_multiple_sharepoint_files",
)
async def upload_multiple_sharepoint_files(
    site_id: str = Query(..., description="SharePoint Site ID"),
    files: list[UploadFile] = File(...),
    folder_path: str = Query("", description="アップロード先のフォルダパス")
) -> list[FileModel]:
    """
    SharePointサイトに複数のファイルを同時にアップロードする
    """
    try:
        files_data = []
        for file in files:
            file_content = await file.read()
            files_data.append((file_content, file.filename or "unknown"))
        
        return msgraphs_repo.sites.upload_multiple_files(site_id, files_data, folder_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"複数ファイルのアップロードに失敗しました: {str(e)}")


@router.get(
    "/files/{file_name}",
    operation_id="download_sharepoint_file",
)
async def download_sharepoint_file(
    file_name: str,
    site_id: str = Query(..., description="SharePoint Site ID"),
    folder_path: str = Query("", description="ファイルがあるフォルダパス")
) -> StreamingResponse:
    """
    SharePointサイトからファイルをダウンロードする
    """
    try:
        file_content = msgraphs_repo.sites.download_file(site_id, file_name, folder_path)
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルのダウンロードに失敗しました: {str(e)}")


@router.get(
    "/files/{file_name}/info",
    response_model=FileModel,
    operation_id="get_sharepoint_file_info",
)
async def get_sharepoint_file_info(
    file_name: str,
    site_id: str = Query(..., description="SharePoint Site ID"),
    folder_path: str = Query("", description="ファイルがあるフォルダパス")
) -> FileModel:
    """
    SharePointサイトのファイル情報を取得する
    """
    try:
        return msgraphs_repo.sites.get_file_info(site_id, file_name, folder_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル情報の取得に失敗しました: {str(e)}")


@router.delete(
    "/files/{file_name}",
    operation_id="delete_sharepoint_file",
)
async def delete_sharepoint_file(
    file_name: str,
    site_id: str = Query(..., description="SharePoint Site ID"),
    folder_path: str = Query("", description="ファイルがあるフォルダパス")
) -> dict:
    """
    SharePointサイトからファイルを削除する
    """
    try:
        success = msgraphs_repo.sites.delete_file(site_id, file_name, folder_path)
        if success:
            return {"message": f"ファイル '{file_name}' を削除しました"}
        else:
            raise HTTPException(status_code=500, detail="ファイルの削除に失敗しました")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルの削除に失敗しました: {str(e)}")


@router.delete(
    "/files/",
    operation_id="delete_multiple_sharepoint_files",
)
async def delete_multiple_sharepoint_files(
    site_id: str = Query(..., description="SharePoint Site ID"),
    file_names: list[str] = Query(..., description="削除するファイル名のリスト"),
    folder_path: str = Query("", description="ファイルがあるフォルダパス")
) -> dict:
    """
    SharePointサイトから複数のファイルを削除する
    """
    try:
        deleted_files = msgraphs_repo.sites.delete_multiple_files(site_id, file_names, folder_path)
        return {
            "message": f"{len(deleted_files)}個のファイルを削除しました",
            "deleted_files": deleted_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"複数ファイルの削除に失敗しました: {str(e)}")