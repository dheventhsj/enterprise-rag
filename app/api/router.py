"""API route registration."""

from fastapi import APIRouter

from app.api.routes import auth, chat, upload

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(upload.router)
api_router.include_router(chat.router)
