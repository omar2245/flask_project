from fastapi import APIRouter, status

from fastapi_app.schemas.auth import RegisterRequest

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    return {
        "message": "User registered successfully",
        "data": {
            "username": payload.username,
            "email": payload.email,
        },
    }
