from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi_app.db.session import get_db
from fastapi_app.dependencies import get_current_user
from fastapi_app.models.user import User
from fastapi_app.schemas.auth import MessageResponse
from fastapi_app.schemas.comment import (
    CommentCreatedResponse,
    CommentCreateRequest,
    CommentLikeUsersResponse,
    CommentUpdateRequest,
)
from fastapi_app.services.comment_service import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    get_comment_like,
    get_comment_like_users,
    like_comment,
    post_exists,
    unlike_comment,
    update_comment,
)

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
)


def validate_pagination(page: int, per_page: int) -> None:
    if page < 1 or per_page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="page and per_page must be greater than 0",
        )


@router.post(
    "", response_model=CommentCreatedResponse, status_code=status.HTTP_201_CREATED
)
def create_comment_endpoint(
    payload: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not post_exists(db=db, post_id=payload.post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    try:
        comment = create_comment(db=db, user_id=current_user.id, payload=payload)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {
        "id": comment.id,
        "user_id": comment.user_id,
        "post_id": comment.post_id,
        "content": comment.content,
        "created_at": comment.created_at,
    }


@router.put("/{comment_id}", response_model=CommentCreatedResponse)
def update_comment_endpoint(
    comment_id: int,
    payload: CommentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = get_comment_by_id(db=db, comment_id=comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    try:
        updated_comment = update_comment(db=db, comment=comment, payload=payload)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {
        "id": updated_comment.id,
        "user_id": updated_comment.user_id,
        "post_id": updated_comment.post_id,
        "content": updated_comment.content,
        "created_at": updated_comment.created_at,
    }


@router.delete("/{comment_id}", response_model=MessageResponse)
def delete_comment_endpoint(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = get_comment_by_id(db=db, comment_id=comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    try:
        delete_comment(db=db, comment=comment)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {"message": "Delete comment successfully"}


@router.post("/{comment_id}/like", response_model=MessageResponse)
def like_comment_endpoint(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not get_comment_by_id(db=db, comment_id=comment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if get_comment_like(db=db, user_id=current_user.id, comment_id=comment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already liked"
        )

    try:
        like_comment(db=db, user_id=current_user.id, comment_id=comment_id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {"message": "Like comment successfully"}


@router.delete("/{comment_id}/like", response_model=MessageResponse)
@router.delete("/{comment_id}/unlike", response_model=MessageResponse)
def unlike_comment_endpoint(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not get_comment_by_id(db=db, comment_id=comment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    like = get_comment_like(db=db, user_id=current_user.id, comment_id=comment_id)

    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not liked this comment",
        )

    try:
        unlike_comment(db=db, like=like)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {"message": "Unlike comment successfully"}


@router.get("/{comment_id}/like", response_model=CommentLikeUsersResponse)
def get_comment_likes_endpoint(
    comment_id: int,
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db),
):
    validate_pagination(page=page, per_page=per_page)

    if not get_comment_by_id(db=db, comment_id=comment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    total, users = get_comment_like_users(
        db=db,
        comment_id=comment_id,
        page=page,
        per_page=per_page,
    )

    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "data": [
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "avatar": user.avatar,
            }
            for user in users
        ],
    }
