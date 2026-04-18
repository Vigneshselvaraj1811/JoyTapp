from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongodb import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.post_service import PostService
from app.services.interaction_service import InteractionService
from app.services.upload_service import UploadService


def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_user_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserService:
    return UserService(db)


def get_post_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> PostService:
    return PostService(db)


def get_interaction_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> InteractionService:
    return InteractionService(db)


def get_upload_service() -> UploadService:
    return UploadService()
