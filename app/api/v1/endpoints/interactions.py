from fastapi import APIRouter, Depends, Query, status

from app.core.security import get_current_user_id
from app.core.dependencies import get_interaction_service
from app.services.interaction_service import InteractionService
from app.schemas.interaction_schema import AddCommentRequest
from app.schemas.common import success_response

router = APIRouter(prefix="/posts", tags=["Interactions"])


@router.post("/{post_id}/like")
async def toggle_like(
    post_id: str,
    user_id: str = Depends(get_current_user_id),
    interaction_service: InteractionService = Depends(get_interaction_service),
):
    result = await interaction_service.toggle_like(post_id, user_id)
    return success_response(message=result["message"], data=result)


@router.post("/{post_id}/comment", status_code=status.HTTP_201_CREATED)
async def add_comment(
    post_id: str,
    payload: AddCommentRequest,
    user_id: str = Depends(get_current_user_id),
    interaction_service: InteractionService = Depends(get_interaction_service),
):
    comment = await interaction_service.add_comment(post_id, user_id, payload)
    return success_response(message="Comment added", data=comment)


@router.get("/{post_id}/comments")
async def get_comments(
    post_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    interaction_service: InteractionService = Depends(get_interaction_service),
):
    result = await interaction_service.get_comments(post_id, page=page, page_size=page_size)
    return success_response(data=result)
