from fastapi import APIRouter, Depends, status

from app.core.security import get_current_user_id
from app.core.dependencies import get_user_service
from app.services.user_service import UserService
from app.schemas.user_schema import UpdateProfileRequest
from app.schemas.common import success_response

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile")
async def get_my_profile(
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_profile(user_id)
    return success_response(data=user)


@router.put("/profile")
async def update_my_profile(
    payload: UpdateProfileRequest,
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.update_profile(user_id, payload)
    return success_response(message="Profile updated", data=user)


@router.put("/profile/image")
async def update_profile_image(
    image_url: str,
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    """Update profile image URL after successful S3 upload."""
    user = await user_service.update_profile_image(user_id, image_url)
    return success_response(message="Profile image updated", data=user)


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_by_id(user_id)
    return success_response(data=user)
