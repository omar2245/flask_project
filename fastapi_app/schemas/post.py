from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from fastapi_app.schemas.user import UserListItemResponse


class PostCreateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"content": "Hello FastAPI"}}
    )

    content: str = Field(min_length=1)
    images: list[str] = Field(default_factory=list, max_length=2)


class PostUpdateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"content": "Updated content"}}
    )

    content: str = Field(min_length=1)


class PostItemResponse(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime
    username: str
    avatar: str | None
    images: list[str]
    likes: int
    is_liked: bool
    comment_count: int


class PostListResponse(BaseModel):
    page: int
    per_page: int
    total: int
    posts: list[PostItemResponse]
    status: str | None = None
    data: dict | None = None


class PostDetailResponse(BaseModel):
    post: PostItemResponse
    status: str | None = None
    data: dict | None = None


class PostCreatedResponse(BaseModel):
    id: int
    message: str


class LikeUsersResponse(BaseModel):
    page: int
    per_page: int
    total: int
    data: list[UserListItemResponse]
