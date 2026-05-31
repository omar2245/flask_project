from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi_app.models.post import Comment, Post, PostImage, PostLikes
from fastapi_app.models.user import User
from fastapi_app.schemas.post import PostCreateRequest, PostUpdateRequest


def get_post_by_id(db: Session, post_id: int) -> Post | None:
    return db.get(Post, post_id)


def create_post(db: Session, user_id: int, payload: PostCreateRequest) -> Post:
    post = Post(user_id=user_id, content=payload.content.strip())

    try:
        db.add(post)
        db.flush()
        for image_url in payload.images:
            db.add(PostImage(post_id=post.id, image_url=image_url))
        db.commit()
        db.refresh(post)
    except SQLAlchemyError:
        db.rollback()
        raise

    return post


def update_post(db: Session, post: Post, payload: PostUpdateRequest) -> Post:
    post.content = payload.content.strip()

    try:
        db.commit()
        db.refresh(post)
    except SQLAlchemyError:
        db.rollback()
        raise

    return post


def delete_post(db: Session, post: Post) -> None:
    try:
        db.delete(post)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def get_posts(db: Session, page: int, per_page: int) -> tuple[int, list[Post]]:
    query = db.query(Post).order_by(Post.created_at.desc())
    total = query.count()
    posts = query.offset((page - 1) * per_page).limit(per_page).all()
    return total, posts


def get_posts_by_user(
    db: Session, user_id: int, page: int, per_page: int
) -> tuple[int, list[Post]]:
    query = (
        db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc())
    )
    total = query.count()
    posts = query.offset((page - 1) * per_page).limit(per_page).all()
    return total, posts


def get_post_like_counts(db: Session, post_ids: list[int]) -> dict[int, int]:
    if not post_ids:
        return {}
    return dict(
        db.query(PostLikes.post_id, func.count(PostLikes.user_id))
        .filter(PostLikes.post_id.in_(post_ids))
        .group_by(PostLikes.post_id)
        .all()
    )


def get_post_comment_counts(db: Session, post_ids: list[int]) -> dict[int, int]:
    if not post_ids:
        return {}
    return dict(
        db.query(Comment.post_id, func.count(Comment.id))
        .filter(Comment.post_id.in_(post_ids))
        .group_by(Comment.post_id)
        .all()
    )


def get_user_liked_post_ids(
    db: Session, user_id: int | None, post_ids: list[int]
) -> set[int]:
    if not user_id or not post_ids:
        return set()
    likes = (
        db.query(PostLikes)
        .filter(PostLikes.user_id == user_id, PostLikes.post_id.in_(post_ids))
        .all()
    )
    return {like.post_id for like in likes}


def get_post_like(db: Session, user_id: int, post_id: int) -> PostLikes | None:
    return (
        db.query(PostLikes)
        .filter(PostLikes.user_id == user_id, PostLikes.post_id == post_id)
        .first()
    )


def like_post(db: Session, user_id: int, post_id: int) -> PostLikes:
    like = PostLikes(user_id=user_id, post_id=post_id)

    try:
        db.add(like)
        db.commit()
        db.refresh(like)
    except SQLAlchemyError:
        db.rollback()
        raise

    return like


def unlike_post(db: Session, like: PostLikes) -> None:
    try:
        db.delete(like)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def get_post_like_users(
    db: Session, post_id: int, page: int, per_page: int
) -> tuple[int, list[User]]:
    query = (
        db.query(User)
        .join(PostLikes, PostLikes.user_id == User.id)
        .filter(PostLikes.post_id == post_id)
    )
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    return total, users
