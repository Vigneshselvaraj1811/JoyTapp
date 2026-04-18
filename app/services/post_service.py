from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
import math

from app.repositories.post_repository import PostRepository
from app.schemas.post_schema import CreatePostRequest, UpdatePostRequest


class PostService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.post_repo = PostRepository(db)

    async def create_post(self, author_id: str, payload: CreatePostRequest) -> dict:
        post = await self.post_repo.insert_one({
            "title": payload.title,
            "content": payload.content,
            "author_id": author_id,
            "tags": payload.tags or [],
            "image_url": payload.image_url,
            "likes_count": 0,
            "comments_count": 0,
            "is_deleted": False,
        })
        return post

    async def get_posts(
        self,
        page: int = 1,
        page_size: int = 10,
        title: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        skip = (page - 1) * page_size
        posts, total = await self.post_repo.get_posts(
            skip=skip, limit=page_size, title=title,
            date_from=date_from, date_to=date_to,
        )
        return {
            "items": posts,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 0,
        }

    async def get_post(self, post_id: str) -> dict:
        post = await self.post_repo.get_by_id_active(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return post

    async def update_post(self, post_id: str, user_id: str, payload: UpdatePostRequest) -> dict:
        post = await self.post_repo.get_by_id_active(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        if post["author_id"] != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this post")

        update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

        return await self.post_repo.update_one(post_id, update_data)

    async def delete_post(self, post_id: str, user_id: str) -> bool:
        post = await self.post_repo.get_by_id_active(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        if post["author_id"] != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")

        await self.post_repo.soft_delete(post_id)
        return True
