from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class File(BaseModel):
    """ファイル情報を表すモデル"""
    
    model_config = ConfigDict(extra="ignore")
    
    name: str
    size: Optional[int] = None
    content_type: Optional[str] = None
    last_modified: Optional[datetime] = None
    url: Optional[str] = None