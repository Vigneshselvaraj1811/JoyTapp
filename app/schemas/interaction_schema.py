from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AddCommentRequest(BaseModel):
    content: str

    class Config:
        str_strip_whitespace = True


class CommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    content: str
    created_at: datetime


class PaginatedCommentsResponse(BaseModel):
    items: List[CommentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LikeResponse(BaseModel):
    post_id: str
    liked: bool
    message: str
