import math
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.interaction_repository import LikeRepository, CommentRepository
from app.repositories.post_repository import PostRepository
from app.schemas.interaction_schema import AddCommentRequest


class InteractionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.like_repo = LikeRepository(db)
        self.comment_repo = CommentRepository(db)
        self.post_repo = PostRepository(db)

    async def toggle_like(self, post_id: str, user_id: str) -> dict:
        post = await self.post_repo.get_by_id_active(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        already_liked = await self.like_repo.has_liked(post_id, user_id)
        if already_liked:
            await self.like_repo.remove_like(post_id, user_id)
            await self.post_repo.increment_like_count(post_id, delta=-1)
            return {"post_id": post_id, "liked": False, "message": "Like removed"}
        else:
            added = await self.like_repo.add_like(post_id, user_id)
            if added:
                await self.post_repo.increment_like_count(post_id, delta=1)
            return {"post_id": post_id, "liked": True, "message": "Post liked"}

    async def add_comment(self, post_id: str, user_id: str, payload: AddCommentRequest) -> dict:
        post = await self.post_repo.get_by_id_active(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        if not payload.content.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment cannot be empty")

        comment = await self.comment_repo.add_comment(post_id, user_id, payload.content.strip())
        await self.post_repo.increment_comment_count(post_id, delta=1)
        return comment

    async def get_comments(self, post_id: str, page: int = 1, page_size: int = 10) -> dict:
        post = await self.post_repo.get_by_id_active(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        skip = (page - 1) * page_size
        comments, total = await self.comment_repo.get_comments(post_id, skip=skip, limit=page_size)
        return {
            "items": comments,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 0,
        }
