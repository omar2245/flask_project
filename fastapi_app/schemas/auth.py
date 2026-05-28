from pydantic import BaseModel, ConfigDict, Field


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
