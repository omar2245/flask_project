from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .post import Post, PostLike, Comment, CommentLike
from .user import User

__all__ = ['db', 'Post', 'PostLike', 'Comment', 'CommentLike', 'User']
