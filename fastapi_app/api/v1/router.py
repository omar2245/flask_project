from fastapi import APIRouter

from fastapi_app.api.v1.endpoints import auth, comments, posts, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(users.legacy_router)
api_router.include_router(posts.router)
api_router.include_router(comments.router)
