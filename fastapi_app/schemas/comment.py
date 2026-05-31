from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from fastapi_app.schemas.user import UserListItemResponse


class CommentCreateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"post_id": 1, "content": "Nice post"}}
    )

    post_id: int
    content: str = Field(min_length=1)


class CommentUpdateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"content": "Updated comment"}}
    )

    content: str = Field(min_length=1)


class CommentItemResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    content: str
    likes: int
    username: str
    avatar: str | None
    is_liked: bool
    created_at: datetime


class CommentListResponse(BaseModel):
    page: int
    per_page: int
    total: int
    comments: list[CommentItemResponse]
    status: str | None = None
    data: dict | None = None


class CommentCreatedResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    content: str
    created_at: datetime


class CommentLikeUsersResponse(BaseModel):
    page: int
    per_page: int
    total: int
    data: list[UserListItemResponse]
