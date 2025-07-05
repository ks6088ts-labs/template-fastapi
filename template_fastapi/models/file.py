from datetime import datetime

from pydantic import BaseModel, ConfigDict


class File(BaseModel):
    """ファイル情報を表すモデル"""

    model_config = ConfigDict(extra="ignore")

    name: str
    size: int | None = None
    content_type: str | None = None
    last_modified: datetime | None = None
    url: str | None = None
