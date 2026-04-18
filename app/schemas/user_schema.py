from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        str_strip_whitespace = True


class PublicUserResponse(BaseModel):
    id: str
    username: str
    full_name: str
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
