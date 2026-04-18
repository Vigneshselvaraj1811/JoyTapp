from fastapi import APIRouter, Depends, status

from app.core.security import get_current_user_id
from app.core.dependencies import get_upload_service
from app.services.upload_service import UploadService
from app.schemas.upload_schema import PresignedUrlRequest
from app.schemas.common import success_response

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/presigned-url", status_code=status.HTTP_200_OK)
async def get_presigned_url(
    payload: PresignedUrlRequest,
    user_id: str = Depends(get_current_user_id),
    upload_service: UploadService = Depends(get_upload_service),
):
    """
    Generate a pre-signed S3 URL for direct client-side file upload.

    Steps:
    1. Call this endpoint to get `upload_url` and `file_url`
    2. PUT your file directly to `upload_url` with the correct `Content-Type` header
    3. Use `file_url` as the permanent file reference in subsequent API calls
    """
    result = await upload_service.generate_presigned_url(payload, user_id)
    return success_response(
        message="Pre-signed URL generated. Upload your file using HTTP PUT to upload_url.",
        data=result,
    )
