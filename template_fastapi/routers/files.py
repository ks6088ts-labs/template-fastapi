import io

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from template_fastapi.models.file import File as FileModel
from template_fastapi.repositories.files import FileRepository

router = APIRouter()
file_repo = FileRepository()


@router.get(
    "/",
    response_model=list[FileModel],
    operation_id="list_files",
)
async def list_files(prefix: str | None = None) -> list[FileModel]:
    """
    ファイル一覧を取得する
    """
    try:
        return file_repo.list_files(prefix=prefix)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル一覧の取得に失敗しました: {str(e)}")


@router.post(
    "/upload",
    response_model=FileModel,
    operation_id="upload_file",
)
async def upload_file(file: UploadFile = File(...)) -> FileModel:
    """
    単一のファイルをアップロードする
    """
    try:
        file_data = await file.read()
        return file_repo.upload_file(file_name=file.filename, file_data=file_data, content_type=file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルのアップロードに失敗しました: {str(e)}")


@router.post(
    "/upload-multiple",
    response_model=list[FileModel],
    operation_id="upload_multiple_files",
)
async def upload_multiple_files(files: list[UploadFile] = File(...)) -> list[FileModel]:
    """
    複数のファイルを同時にアップロードする
    """
    try:
        file_data_list = []
        for file in files:
            file_data = await file.read()
            file_data_list.append((file.filename, file_data, file.content_type))

        return file_repo.upload_files(file_data_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"複数ファイルのアップロードに失敗しました: {str(e)}")


@router.get(
    "/{file_name}",
    operation_id="download_file",
)
async def download_file(file_name: str):
    """
    ファイルをダウンロードする
    """
    try:
        file_data = file_repo.download_file(file_name)
        file_info = file_repo.get_file_info(file_name)

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
    "/{file_name}/info",
    response_model=FileModel,
    operation_id="get_file_info",
)
async def get_file_info(file_name: str) -> FileModel:
    """
    ファイル情報を取得する
    """
    try:
        return file_repo.get_file_info(file_name)
    except Exception as e:
        if "見つかりません" in str(e):
            raise HTTPException(status_code=404, detail=f"ファイル '{file_name}' が見つかりません")
        raise HTTPException(status_code=500, detail=f"ファイル情報の取得に失敗しました: {str(e)}")


@router.delete(
    "/{file_name}",
    operation_id="delete_file",
)
async def delete_file(file_name: str) -> dict:
    """
    ファイルを削除する
    """
    try:
        file_repo.delete_file(file_name)
        return {"message": f"ファイル '{file_name}' を正常に削除しました"}
    except Exception as e:
        if "見つかりません" in str(e):
            raise HTTPException(status_code=404, detail=f"ファイル '{file_name}' が見つかりません")
        raise HTTPException(status_code=500, detail=f"ファイルの削除に失敗しました: {str(e)}")


@router.delete(
    "/",
    operation_id="delete_multiple_files",
)
async def delete_multiple_files(file_names: list[str]) -> dict:
    """
    複数のファイルを同時に削除する
    """
    try:
        deleted_files = file_repo.delete_files(file_names)
        return {"message": f"{len(deleted_files)} 個のファイルを正常に削除しました", "deleted_files": deleted_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"複数ファイルの削除に失敗しました: {str(e)}")
