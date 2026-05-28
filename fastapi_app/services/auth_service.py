import bcrypt
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi_app.models.user import User
from fastapi_app.schemas.auth import RegisterRequest, LoginRequest


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def register_user(db: Session, payload: RegisterRequest) -> User:
    password_hash = hash_password(payload.password)
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=password_hash,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except SQLAlchemyError:
        db.rollback()
        raise

    return user


def authenticate_user(db: Session, payload: LoginRequest) -> User | None:
    user = get_user_by_login(db=db, account=payload.username)

    if not user:
        return None
    if not verify_password(payload.password, user.password_hash):
        return None

    return user


def get_user_by_username_or_email(
    db: Session, username: str, email: str
) -> User | None:
    return (
        db.query(User)
        .filter(or_(User.username == username, User.email == email))
        .first()
    )


def get_user_by_login(db: Session, account: str) -> User | None:
    return (
        db.query(User)
        .filter(or_(User.username == account, User.email == account))
        .first()
    )


def verify_password(password: str, password_hash: str) -> bool:
    password_bytes = password.encode("utf-8")
    password_hash_bytes = password_hash.encode("utf-8")
    return bcrypt.checkpw(password_bytes, password_hash_bytes)
