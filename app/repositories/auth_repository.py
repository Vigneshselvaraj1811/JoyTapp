from typing import Optional, Dict
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.base import BaseRepository, serialize_doc


class AuthRepository(BaseRepository):
    collection_name = "refresh_tokens"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def save_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> Dict:
        return await self.insert_one({
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at,
            "is_revoked": False,
        })

    async def find_valid_token(self, token: str) -> Optional[Dict]:
        doc = await self.collection.find_one({
            "token": token,
            "is_revoked": False,
            "expires_at": {"$gt": datetime.now(timezone.utc)},
        })
        return serialize_doc(doc) if doc else None

    async def revoke_token(self, token: str) -> bool:
        result = await self.collection.update_one(
            {"token": token},
            {"$set": {"is_revoked": True}}
        )
        return result.modified_count > 0

    async def revoke_all_user_tokens(self, user_id: str) -> int:
        result = await self.collection.update_many(
            {"user_id": user_id, "is_revoked": False},
            {"$set": {"is_revoked": True}}
        )
        return result.modified_count
