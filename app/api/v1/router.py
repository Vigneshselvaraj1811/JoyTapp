from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, posts, interactions, uploads

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(posts.router)
api_router.include_router(interactions.router)
api_router.include_router(uploads.router)