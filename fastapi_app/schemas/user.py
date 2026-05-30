from pydantic import BaseModel, ConfigDict, Field


class UserMeResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None
    avatar: str | None
    desc: str | None


class UserPublicResponse(BaseModel):
    id: int
    username: str
    full_name: str | None
    avatar: str | None
    desc: str | None


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "omar",
                "email": "new@example.com",
                "full_name": "Omar Chen",
                "desc": "Backend learner",
            }
        }
    )

    username: str | None = Field(default=None, min_length=3, max_length=20)
    email: str | None = Field(default=None, pattern=r"^\S+@\S+\.\S+$")
    full_name: str | None = Field(default=None, max_length=100)
    desc: str | None = Field(default=None, max_length=255)


class FollowStatsResponse(BaseModel):
    followers_count: int
    following_count: int


class UserListItemResponse(BaseModel):
    id: int
    username: str
    full_name: str | None
    avatar: str | None


class UserListResponse(BaseModel):
    page: int
    per_page: int
    total: int
    data: list[UserListItemResponse]


class IsFollowingResponse(BaseModel):
    is_following: bool
