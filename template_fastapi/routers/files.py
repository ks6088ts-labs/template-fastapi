import io

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from template_fastapi.models.file import File as FileModel
from template_fastapi.repositories.files import FileRepository
from template_fastapi.settings.logging import get_logger

logger = get_logger(__name__)
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
    logger.info(f"Listing files with prefix: {prefix}")
    try:
        files = file_repo.list_files(prefix=prefix)
        logger.info(f"Found {len(files)} files")
        return files
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}", exc_info=True)
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
    logger.info(f"Uploading file: {file.filename} (content_type: {file.content_type})")
    try:
        file_data = await file.read()
        logger.debug(f"File size: {len(file_data)} bytes")
        result = file_repo.upload_file(file_name=file.filename, file_data=file_data, content_type=file.content_type)
        logger.info(f"Successfully uploaded file: {file.filename}")
        return result
    except Exception as e:
        logger.error(f"Failed to upload file {file.filename}: {str(e)}", exc_info=True)
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
    logger.info(f"Uploading {len(files)} files")
    try:
        file_data_list = []
        for file in files:
            file_data = await file.read()
            logger.debug(f"Processing file: {file.filename} ({len(file_data)} bytes)")
            file_data_list.append((file.filename, file_data, file.content_type))

        result = file_repo.upload_files(file_data_list)
        logger.info(f"Successfully uploaded {len(result)} files")
        return result
    except Exception as e:
        logger.error(f"Failed to upload multiple files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"複数ファイルのアップロードに失敗しました: {str(e)}")


@router.get(
    "/{file_name}",
    operation_id="download_file",
)
async def download_file(file_name: str):
    """
    ファイルをダウンロードする
    """
    logger.info(f"Downloading file: {file_name}")
    try:
        file_data = file_repo.download_file(file_name)
        file_info = file_repo.get_file_info(file_name)
        logger.debug(f"File download prepared: {file_name} ({len(file_data)} bytes)")

        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=file_info.content_type or "application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
    except Exception as e:
        if "見つかりません" in str(e):
            logger.warning(f"File not found: {file_name}")
            raise HTTPException(status_code=404, detail=f"ファイル '{file_name}' が見つかりません")
        logger.error(f"Failed to download file {file_name}: {str(e)}", exc_info=True)
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
    logger.info(f"Getting file info for: {file_name}")
    try:
        file_info = file_repo.get_file_info(file_name)
        logger.debug(f"File info retrieved: {file_name}")
        return file_info
    except Exception as e:
        if "見つかりません" in str(e):
            logger.warning(f"File not found: {file_name}")
            raise HTTPException(status_code=404, detail=f"ファイル '{file_name}' が見つかりません")
        logger.error(f"Failed to get file info for {file_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ファイル情報の取得に失敗しました: {str(e)}")


@router.delete(
    "/{file_name}",
    operation_id="delete_file",
)
async def delete_file(file_name: str) -> dict:
    """
    ファイルを削除する
    """
    logger.info(f"Deleting file: {file_name}")
    try:
        file_repo.delete_file(file_name)
        logger.info(f"Successfully deleted file: {file_name}")
        return {"message": f"ファイル '{file_name}' を正常に削除しました"}
    except Exception as e:
        if "見つかりません" in str(e):
            logger.warning(f"File not found for deletion: {file_name}")
            raise HTTPException(status_code=404, detail=f"ファイル '{file_name}' が見つかりません")
        logger.error(f"Failed to delete file {file_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ファイルの削除に失敗しました: {str(e)}")


@router.delete(
    "/",
    operation_id="delete_multiple_files",
)
async def delete_multiple_files(file_names: list[str]) -> dict:
    """
    複数のファイルを同時に削除する
    """
    logger.info(f"Deleting {len(file_names)} files: {file_names}")
    try:
        deleted_files = file_repo.delete_files(file_names)
        logger.info(f"Successfully deleted {len(deleted_files)} files")
        return {"message": f"{len(deleted_files)} 個のファイルを正常に削除しました", "deleted_files": deleted_files}
    except Exception as e:
        logger.error(f"Failed to delete multiple files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"複数ファイルの削除に失敗しました: {str(e)}")
