from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_refresh_token,
)
from app.repositories.user_repository import UserRepository
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.user_repo = UserRepository(db)
        self.auth_repo = AuthRepository(db)

    async def register(self, payload: RegisterRequest) -> dict:
        if await self.user_repo.email_exists(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        if await self.user_repo.username_exists(payload.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

        user = await self.user_repo.insert_one({
            "username": payload.username.lower(),
            "email": payload.email.lower(),
            "password_hash": hash_password(payload.password),
            "full_name": payload.full_name,
            "bio": None,
            "profile_image_url": None,
            "is_active": True,
        })

        tokens = await self._generate_tokens(user["id"])
        return {"user": user, **tokens}

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user = await self.user_repo.find_by_email(payload.email)
        if not user or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.get("is_active"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

        return await self._generate_tokens(user["id"])

    async def refresh_token(self, token: str) -> dict:
        payload = decode_refresh_token(token)
        db_token = await self.auth_repo.find_valid_token(token)
        if not db_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid or expired")

        user_id = payload.get("sub")
        await self.auth_repo.revoke_token(token)
        return await self._generate_tokens(user_id)

    async def logout(self, refresh_token: str) -> bool:
        return await self.auth_repo.revoke_token(refresh_token)

    async def _generate_tokens(self, user_id: str) -> dict:
        access_token = create_access_token({"sub": user_id})
        refresh_token = create_refresh_token({"sub": user_id})

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.auth_repo.save_refresh_token(user_id, refresh_token, expires_at)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
