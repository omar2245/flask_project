from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi_app.models.post import Comment, CommentLikes, Post
from fastapi_app.models.user import User
from fastapi_app.schemas.comment import CommentCreateRequest, CommentUpdateRequest


def get_comment_by_id(db: Session, comment_id: int) -> Comment | None:
    return db.get(Comment, comment_id)


def create_comment(db: Session, user_id: int, payload: CommentCreateRequest) -> Comment:
    comment = Comment(
        user_id=user_id,
        post_id=payload.post_id,
        content=payload.content.strip(),
    )

    try:
        db.add(comment)
        db.commit()
        db.refresh(comment)
    except SQLAlchemyError:
        db.rollback()
        raise

    return comment


def update_comment(
    db: Session, comment: Comment, payload: CommentUpdateRequest
) -> Comment:
    comment.content = payload.content.strip()

    try:
        db.commit()
        db.refresh(comment)
    except SQLAlchemyError:
        db.rollback()
        raise

    return comment


def delete_comment(db: Session, comment: Comment) -> None:
    try:
        db.delete(comment)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def get_post_comments(
    db: Session, post_id: int, page: int, per_page: int
) -> tuple[int, list[Comment]]:
    query = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
    )
    total = query.count()
    comments = query.offset((page - 1) * per_page).limit(per_page).all()
    return total, comments


def get_user_liked_comment_ids(
    db: Session, user_id: int | None, comment_ids: list[int]
) -> set[int]:
    if not user_id or not comment_ids:
        return set()
    likes = (
        db.query(CommentLikes)
        .filter(
            CommentLikes.user_id == user_id,
            CommentLikes.comment_id.in_(comment_ids),
        )
        .all()
    )
    return {like.comment_id for like in likes}


def get_comment_like(db: Session, user_id: int, comment_id: int) -> CommentLikes | None:
    return (
        db.query(CommentLikes)
        .filter(CommentLikes.user_id == user_id, CommentLikes.comment_id == comment_id)
        .first()
    )


def like_comment(db: Session, user_id: int, comment_id: int) -> CommentLikes:
    like = CommentLikes(user_id=user_id, comment_id=comment_id)

    try:
        db.add(like)
        db.commit()
        db.refresh(like)
    except SQLAlchemyError:
        db.rollback()
        raise

    return like


def unlike_comment(db: Session, like: CommentLikes) -> None:
    try:
        db.delete(like)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def get_comment_like_users(
    db: Session, comment_id: int, page: int, per_page: int
) -> tuple[int, list[User]]:
    query = (
        db.query(User)
        .join(CommentLikes, CommentLikes.user_id == User.id)
        .filter(CommentLikes.comment_id == comment_id)
    )
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    return total, users


def post_exists(db: Session, post_id: int) -> bool:
    return db.get(Post, post_id) is not None
