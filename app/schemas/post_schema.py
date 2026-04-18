from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CreatePostRequest(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    image_url: Optional[str] = None

    class Config:
        str_strip_whitespace = True


class UpdatePostRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None

    class Config:
        str_strip_whitespace = True


class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    tags: List[str] = []
    image_url: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime


class PaginatedPostsResponse(BaseModel):
    items: List[PostResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
