from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi_app.models.follow import Follow
from fastapi_app.models.user import User


def get_follow(
    db: Session,
    follower_id: int,
    following_id: int,
) -> Follow | None:
    return (
        db.query(Follow)
        .filter(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id,
        )
        .first()
    )


def follow_user(
    db: Session,
    follower_id: int,
    following_id: int,
) -> Follow:
    follow = Follow(
        follower_id=follower_id,
        following_id=following_id,
    )

    try:
        db.add(follow)
        db.commit()
        db.refresh(follow)
    except SQLAlchemyError:
        db.rollback()
        raise

    return follow


def unfollow_user(db: Session, follow: Follow) -> None:
    try:
        db.delete(follow)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


def get_follow_stats(db: Session, user_id: int) -> dict[str, int]:
    followers_count = db.query(Follow).filter(Follow.following_id == user_id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == user_id).count()

    return {
        "followers_count": followers_count,
        "following_count": following_count,
    }


def user_exists(db: Session, user_id: int) -> bool:
    return db.get(User, user_id) is not None
