from pydantic import BaseModel, ConfigDict, field_validator, Field


class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "omar",
                "email": "omar@example.com",
                "password": "abc12345",
            }
        }
    )
    username: str = Field(min_length=3, max_length=20)
    email: str = Field(..., pattern=r"^\S+@\S+\.\S+$")
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        has_letter = any(char.isalpha() for char in value)
        has_number = any(char.isdigit() for char in value)
        if not has_letter or not has_number:
            raise ValueError("Password must contain both letters and numbers")
        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "omar",
                "password": "abc12345",
            }
        }
    )
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserMeResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None
    avatar: str | None
    desc: str | None


class AccessTokenResponse(BaseModel):
    access_token: str


class MessageResponse(BaseModel):
    message: str
