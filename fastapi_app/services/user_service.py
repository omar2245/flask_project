from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi_app.models.user import User
from fastapi_app.schemas.user import UserUpdateRequest


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_conflict_for_update(
    db: Session, user_id: int, username: str | None, email: str | None
) -> User | None:
    conditions = []

    if username:
        conditions.append(User.username == username)

    if email:
        conditions.append(User.email == email)

    if not conditions:
        return None

    return db.query(User).filter(or_(*conditions), User.id != user_id).first()


def update_user(db: Session, user: User, payload: UserUpdateRequest) -> User:
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError:
        db.rollback()
        raise

    return user
