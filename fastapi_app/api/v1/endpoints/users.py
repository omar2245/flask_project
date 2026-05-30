from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi_app.db.session import get_db
from fastapi_app.dependencies import get_current_user
from fastapi_app.models.user import User
from fastapi_app.schemas.auth import MessageResponse
from fastapi_app.schemas.user import (
    FollowStatsResponse,
    UserMeResponse,
    UserPublicResponse,
    UserUpdateRequest,
)
from fastapi_app.services.follow_service import (
    follow_user,
    get_follow,
    get_follow_stats,
    unfollow_user,
    user_exists,
)
from fastapi_app.services.user_service import (
    get_user_by_id,
    get_user_conflict_for_update,
    update_user,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


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


@router.get("/{user_id}", response_model=UserPublicResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db=db, user_id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "avatar": user.avatar,
        "desc": user.desc,
    }


@router.put("/me", response_model=UserMeResponse)
def update_me(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conflict_user = get_user_conflict_for_update(
        db=db,
        user_id=current_user.id,
        username=payload.username,
        email=payload.email,
    )

    if conflict_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    try:
        updated_user = update_user(
            db=db,
            user=current_user,
            payload=payload,
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {
        "id": updated_user.id,
        "username": updated_user.username,
        "email": updated_user.email,
        "full_name": updated_user.full_name,
        "avatar": updated_user.avatar,
        "desc": updated_user.desc,
    }


@router.post("/{user_id}/follow", response_model=MessageResponse)
def follow(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself",
        )

    if not user_exists(db=db, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing_follow = get_follow(
        db=db,
        follower_id=current_user.id,
        following_id=user_id,
    )

    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already followed",
        )

    try:
        follow_user(
            db=db,
            follower_id=current_user.id,
            following_id=user_id,
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {"message": "Follow successfully"}


@router.delete("/{user_id}/follow", response_model=MessageResponse)
def unfollow(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot unfollow yourself",
        )

    if not user_exists(db=db, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    follow = get_follow(
        db=db,
        follower_id=current_user.id,
        following_id=user_id,
    )

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not following this user",
        )

    try:
        unfollow_user(db=db, follow=follow)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {"message": "Unfollow successfully"}


@router.get("/{user_id}/follow-stats", response_model=FollowStatsResponse)
def follow_stats(user_id: int, db: Session = Depends(get_db)):
    if not user_exists(db=db, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return get_follow_stats(db=db, user_id=user_id)
