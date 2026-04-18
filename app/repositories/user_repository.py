from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    collection_name = "users"

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)

    async def find_by_email(self, email: str) -> Optional[Dict]:
        return await self.find_one({"email": email.lower()})

    async def find_by_username(self, username: str) -> Optional[Dict]:
        return await self.find_one({"username": username.lower()})

    async def email_exists(self, email: str) -> bool:
        count = await self.count({"email": email.lower()})
        return count > 0

    async def username_exists(self, username: str) -> bool:
        count = await self.count({"username": username.lower()})
        return count > 0

    async def update_profile_image(self, user_id: str, image_url: str) -> Optional[Dict]:
        return await self.update_one(user_id, {"profile_image_url": image_url})
