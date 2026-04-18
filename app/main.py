from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.v1.router import api_router
from app.core.exceptions import (
    validation_exception_handler,
    duplicate_key_exception_handler,
    generic_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="Production-grade backend API with FastAPI, MongoDB, JWT Auth & AWS S3",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(DuplicateKeyError, duplicate_key_exception_handler)
    application.add_exception_handler(Exception, generic_exception_handler)

    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}
