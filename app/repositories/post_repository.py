from typing import Optional, Dict, List, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from app.repositories.base import BaseRepository, serialize_doc, to_object_id


class PostRepository(BaseRepository):
    collection_name = "posts"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    def _active_query(self) -> Dict:
        return {"is_deleted": {"$ne": True}}

    async def get_posts(
        self,
        skip: int = 0,
        limit: int = 10,
        title: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        author_id: Optional[str] = None,
    ) -> Tuple[List[Dict], int]:
        query = self._active_query()
        if title:
            query["title"] = {"$regex": title, "$options": "i"}
        if date_from or date_to:
            query["created_at"] = {}
            if date_from:
                query["created_at"]["$gte"] = date_from
            if date_to:
                query["created_at"]["$lte"] = date_to
        if author_id:
            query["author_id"] = author_id

        total = await self.count(query)
        posts = await self.find_many(query, skip=skip, limit=limit)
        return posts, total

    async def get_by_id_active(self, post_id: str) -> Optional[Dict]:
        oid = to_object_id(post_id)
        if not oid:
            return None
        query = {"_id": oid, **self._active_query()}
        doc = await self.collection.find_one(query)
        return serialize_doc(doc) if doc else None

    async def get_by_author(self, author_id: str) -> List[Dict]:
        query = {"author_id": author_id, **self._active_query()}
        return await self.find_many(query)

    async def increment_like_count(self, post_id: str, delta: int = 1):
        oid = to_object_id(post_id)
        if oid:
            await self.collection.update_one(
                {"_id": oid},
                {"$inc": {"likes_count": delta}}
            )

    async def increment_comment_count(self, post_id: str, delta: int = 1):
        oid = to_object_id(post_id)
        if oid:
            await self.collection.update_one(
                {"_id": oid},
                {"$inc": {"comments_count": delta}}
            )
