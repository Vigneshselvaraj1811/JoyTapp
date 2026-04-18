from pydantic import BaseModel
from typing import Optional


class PresignedUrlRequest(BaseModel):
    filename: str
    content_type: str
    file_size_bytes: int
    folder: Optional[str] = "uploads"


class PresignedUrlResponse(BaseModel):
    upload_url: str
    file_url: str
    key: str
    expires_in: int
