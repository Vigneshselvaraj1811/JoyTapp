from typing import Optional, Dict, List, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from app.repositories.base import BaseRepository, serialize_doc


class LikeRepository(BaseRepository):
    collection_name = "likes"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def add_like(self, post_id: str, user_id: str) -> bool:
        """Returns True if like added, False if already liked (duplicate)."""
        try:
            await self.insert_one({"post_id": post_id, "user_id": user_id})
            return True
        except DuplicateKeyError:
            return False

    async def remove_like(self, post_id: str, user_id: str) -> bool:
        result = await self.collection.delete_one({"post_id": post_id, "user_id": user_id})
        return result.deleted_count > 0

    async def has_liked(self, post_id: str, user_id: str) -> bool:
        count = await self.count({"post_id": post_id, "user_id": user_id})
        return count > 0

    async def get_like_count(self, post_id: str) -> int:
        return await self.count({"post_id": post_id})


class CommentRepository(BaseRepository):
    collection_name = "comments"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def add_comment(self, post_id: str, user_id: str, content: str) -> Dict:
        return await self.insert_one({
            "post_id": post_id,
            "user_id": user_id,
            "content": content,
            "is_deleted": False,
        })

    async def get_comments(
        self, post_id: str, skip: int = 0, limit: int = 10
    ) -> Tuple[List[Dict], int]:
        query = {"post_id": post_id, "is_deleted": {"$ne": True}}
        total = await self.count(query)
        comments = await self.find_many(query, skip=skip, limit=limit)
        return comments, total

    async def delete_comment(self, comment_id: str, user_id: str) -> bool:
        from app.repositories.base import to_object_id
        oid = to_object_id(comment_id)
        if not oid:
            return False
        result = await self.collection.update_one(
            {"_id": oid, "user_id": user_id},
            {"$set": {"is_deleted": True}}
        )
        return result.modified_count > 0
