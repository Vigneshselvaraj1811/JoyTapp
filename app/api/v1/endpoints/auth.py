from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_auth_service
from app.services.auth_service import AuthService
from app.schemas.auth_schema import (
    RegisterRequest, LoginRequest,
    RefreshTokenRequest, LogoutRequest)
from app.schemas.common import success_response

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = await auth_service.register(payload)
    user = result.pop("user")
    user.pop("password_hash", None)
    return success_response(
        message="Registration successful",
        data={"user": user, "tokens": result},
    )


@router.post("/login")
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    tokens = await auth_service.login(payload)
    return success_response(message="Login successful", data=tokens)


@router.post("/refresh-token")
async def refresh_token(
    payload: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    tokens = await auth_service.refresh_token(payload.refresh_token)
    return success_response(message="Token refreshed", data=tokens)


@router.post("/logout")
async def logout(
    payload: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout(payload.refresh_token)
    return success_response(message="Logged out successfully")
