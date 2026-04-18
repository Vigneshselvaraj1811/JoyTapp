from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UpdateProfileRequest


class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.user_repo = UserRepository(db)

    async def get_profile(self, user_id: str) -> dict:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.pop("password_hash", None)
        return user

    async def update_profile(self, user_id: str, payload: UpdateProfileRequest) -> dict:
        update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

        user = await self.user_repo.update_one(user_id, update_data)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.pop("password_hash", None)
        return user

    async def get_user_by_id(self, user_id: str) -> dict:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        # Return only public fields
        return {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "bio": user.get("bio"),
            "profile_image_url": user.get("profile_image_url"),
        }

    async def update_profile_image(self, user_id: str, image_url: str) -> dict:
        user = await self.user_repo.update_profile_image(user_id, image_url)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.pop("password_hash", None)
        return user
