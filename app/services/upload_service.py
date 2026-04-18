import uuid
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.upload_schema import PresignedUrlRequest, PresignedUrlResponse


class UploadService:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                self._client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION,
                )
            except NoCredentialsError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="AWS credentials not configured"
                )
        return self._client

    def _validate_request(self, payload: PresignedUrlRequest):
        if payload.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{payload.content_type}' not allowed. Allowed: {settings.ALLOWED_FILE_TYPES}",
            )
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if payload.file_size_bytes > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit",
            )

    def _build_s3_key(self, folder: str, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        folder = folder.strip("/")
        return f"{folder}/{unique_name}"

    async def generate_presigned_url(self, payload: PresignedUrlRequest, user_id: str) -> PresignedUrlResponse:
        self._validate_request(payload)

        s3_key = self._build_s3_key(f"{payload.folder}/{user_id}", payload.filename)
        client = self._get_client()

        try:
            presigned_url = client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": settings.AWS_S3_BUCKET_NAME,
                    "Key": s3_key,
                    "ContentType": payload.content_type,
                    "ContentLength": payload.file_size_bytes,
                },
                ExpiresIn=settings.S3_PRESIGNED_URL_EXPIRY,
            )
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not generate upload URL: {str(e)}",
            )

        file_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"

        return PresignedUrlResponse(
            upload_url=presigned_url,
            file_url=file_url,
            key=s3_key,
            expires_in=settings.S3_PRESIGNED_URL_EXPIRY,
        )
