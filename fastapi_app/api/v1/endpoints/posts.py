from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi_app.db.session import get_db
from fastapi_app.dependencies import get_current_user, get_optional_current_user_id
from fastapi_app.models.post import Post
from fastapi_app.models.user import User
from fastapi_app.schemas.auth import MessageResponse
from fastapi_app.schemas.comment import CommentListResponse
from fastapi_app.schemas.post import (
    LikeUsersResponse,
    PostCreateRequest,
    PostCreatedResponse,
    PostDetailResponse,
    PostItemResponse,
    PostListResponse,
    PostUpdateRequest,
)
from fastapi_app.services.comment_service import (
    get_post_comments,
    get_user_liked_comment_ids,
)
from fastapi_app.services.post_service import (
    create_post,
    delete_post,
    get_post_by_id,
    get_post_comment_counts,
    get_post_like,
    get_post_like_counts,
    get_post_like_users,
    get_posts,
    get_user_liked_post_ids,
    like_post,
    unlike_post,
    update_post,
)

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


def serialize_post(
    post: Post,
    likes_count: int,
    comment_count: int,
    is_liked: bool,
) -> dict:
    return {
        "id": post.id,
        "user_id": post.user_id,
        "content": post.content,
        "created_at": post.created_at,
        "username": post.user.username,
        "avatar": post.user.avatar,
        "images": [image.image_url for image in post.images],
        "likes": likes_count,
        "is_liked": is_liked,
        "comment_count": comment_count,
    }


def validate_pagination(page: int, per_page: int) -> None:
    if page < 1 or per_page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="page and per_page must be greater than 0",
        )


@router.post(
    "", response_model=PostCreatedResponse, status_code=status.HTTP_201_CREATED
)
def create_post_endpoint(
    payload: PostCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        post = create_post(db=db, user_id=current_user.id, payload=payload)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {"id": post.id, "message": "Create post successfully"}


@router.get("", response_model=PostListResponse)
def get_posts_endpoint(
    page: int = 1,
    per_page: int = 10,
    limit: int | None = None,
    current_user_id: int | None = Depends(get_optional_current_user_id),
    db: Session = Depends(get_db),
):
    if limit is not None:
        per_page = limit

    validate_pagination(page=page, per_page=per_page)

    total, posts = get_posts(db=db, page=page, per_page=per_page)
    post_ids = [post.id for post in posts]
    likes_counts = get_post_like_counts(db=db, post_ids=post_ids)
    comment_counts = get_post_comment_counts(db=db, post_ids=post_ids)
    liked_post_ids = get_user_liked_post_ids(
        db=db,
        user_id=current_user_id,
        post_ids=post_ids,
    )

    post_items = [
        serialize_post(
            post=post,
            likes_count=likes_counts.get(post.id, 0),
            comment_count=comment_counts.get(post.id, 0),
            is_liked=post.id in liked_post_ids,
        )
        for post in posts
    ]

    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "posts": post_items,
        "status": "success",
        "data": {
            "page": page,
            "per_page": per_page,
            "total_post": total,
            "posts": post_items,
        },
    }


@router.get("/{post_id}", response_model=PostDetailResponse)
def get_post_detail_endpoint(
    post_id: int,
    current_user_id: int | None = Depends(get_optional_current_user_id),
    db: Session = Depends(get_db),
):
    post = get_post_by_id(db=db, post_id=post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    likes_counts = get_post_like_counts(db=db, post_ids=[post.id])
    comment_counts = get_post_comment_counts(db=db, post_ids=[post.id])
    liked_post_ids = get_user_liked_post_ids(
        db=db,
        user_id=current_user_id,
        post_ids=[post.id],
    )

    post_item = serialize_post(
        post=post,
        likes_count=likes_counts.get(post.id, 0),
        comment_count=comment_counts.get(post.id, 0),
        is_liked=post.id in liked_post_ids,
    )

    return {"post": post_item, "status": "success", "data": {"post": post_item}}


@router.put("/{post_id}", response_model=MessageResponse)
def update_post_endpoint(
    post_id: int,
    payload: PostUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post_by_id(db=db, post_id=post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    try:
        update_post(db=db, post=post, payload=payload)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {"message": "Update post successfully"}


@router.delete("/{post_id}", response_model=MessageResponse)
def delete_post_endpoint(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post_by_id(db=db, post_id=post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )

    try:
        delete_post(db=db, post=post)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {"message": "Delete post successfully"}


@router.get("/{post_id}/comments", response_model=CommentListResponse)
def get_post_comments_endpoint(
    post_id: int,
    page: int = 1,
    per_page: int = 10,
    limit: int | None = None,
    current_user_id: int | None = Depends(get_optional_current_user_id),
    db: Session = Depends(get_db),
):
    if limit is not None:
        per_page = limit

    validate_pagination(page=page, per_page=per_page)

    if not get_post_by_id(db=db, post_id=post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    total, comments = get_post_comments(
        db=db,
        post_id=post_id,
        page=page,
        per_page=per_page,
    )
    comment_ids = [comment.id for comment in comments]
    liked_comment_ids = get_user_liked_comment_ids(
        db=db,
        user_id=current_user_id,
        comment_ids=comment_ids,
    )

    comment_items = [
        {
            "id": comment.id,
            "user_id": comment.user_id,
            "post_id": comment.post_id,
            "content": comment.content,
            "likes": len(comment.likes),
            "username": comment.user.username,
            "avatar": comment.user.avatar,
            "is_liked": comment.id in liked_comment_ids,
            "created_at": comment.created_at,
        }
        for comment in comments
    ]

    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "comments": comment_items,
        "status": "success",
        "data": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "comments": comment_items,
        },
    }


@router.post("/{post_id}/like", response_model=MessageResponse)
def like_post_endpoint(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not get_post_by_id(db=db, post_id=post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if get_post_like(db=db, user_id=current_user.id, post_id=post_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already liked"
        )

    try:
        like_post(db=db, user_id=current_user.id, post_id=post_id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {"message": "Like post successfully"}


@router.delete("/{post_id}/like", response_model=MessageResponse)
@router.delete("/{post_id}/unlike", response_model=MessageResponse)
def unlike_post_endpoint(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not get_post_by_id(db=db, post_id=post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    like = get_post_like(db=db, user_id=current_user.id, post_id=post_id)

    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not liked this post",
        )

    try:
        unlike_post(db=db, like=like)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return {"message": "Unlike post successfully"}


@router.get("/{post_id}/like", response_model=LikeUsersResponse)
def get_post_likes_endpoint(
    post_id: int,
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db),
):
    validate_pagination(page=page, per_page=per_page)

    if not get_post_by_id(db=db, post_id=post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    total, users = get_post_like_users(
        db=db,
        post_id=post_id,
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
