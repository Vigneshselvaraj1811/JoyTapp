from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status

from app.core.security import get_current_user_id
from app.core.dependencies import get_post_service
from app.core.config import settings
from app.services.post_service import PostService
from app.schemas.post_schema import CreatePostRequest, UpdatePostRequest
from app.schemas.common import success_response

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: CreatePostRequest,
    user_id: str = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    post = await post_service.create_post(user_id, payload)
    return success_response(message="Post created", data=post)


@router.get("")
async def list_posts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    title: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    post_service: PostService = Depends(get_post_service),
):
    result = await post_service.get_posts(
        page=page, page_size=page_size,
        title=title, date_from=date_from, date_to=date_to,
    )
    return success_response(data=result)


@router.get("/{post_id}")
async def get_post(
    post_id: str,
    post_service: PostService = Depends(get_post_service),
):
    post = await post_service.get_post(post_id)
    return success_response(data=post)


@router.put("/{post_id}")
async def update_post(
    post_id: str,
    payload: UpdatePostRequest,
    user_id: str = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    post = await post_service.update_post(post_id, user_id, payload)
    return success_response(message="Post updated", data=post)


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(
    post_id: str,
    user_id: str = Depends(get_current_user_id),
    post_service: PostService = Depends(get_post_service),
):
    await post_service.delete_post(post_id, user_id)
    return success_response(message="Post deleted successfully")
