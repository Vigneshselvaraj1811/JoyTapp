from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "JoyTapp Backend API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["*"]

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "joytapp_db"

    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_REFRESH_SECRET_KEY: str = "your-refresh-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET_NAME: str = "joytapp-uploads"
    S3_PRESIGNED_URL_EXPIRY: int = 3600  # 1 hour

    # Upload Restrictions
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/gif", "application/pdf"]
    MAX_FILE_SIZE_MB: int = 10

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
