from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi_app.db.session import get_db
from fastapi_app.dependencies import get_current_user, get_refresh_user_id
from fastapi_app.models.user import User
from fastapi_app.core.security import create_access_token, create_refresh_token
from fastapi_app.schemas.auth import (
    MessageResponse,
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserMeResponse,
    AccessTokenResponse,
)
from fastapi_app.services.auth_service import (
    authenticate_user,
    get_user_by_username_or_email,
    register_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = get_user_by_username_or_email(
        db=db,
        username=payload.username,
        email=payload.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    try:
        register_user(db=db, payload=payload)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db=db, payload=payload)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar": current_user.avatar,
        "desc": current_user.desc,
    }


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(user_id: int = Depends(get_refresh_user_id)):
    access_token = create_access_token(user_id=user_id)
    return {"access_token": access_token}
