from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .post import Post, Comment, PostLikes, CommentLikes
from .user import User

__all__ = ['db', 'Post', 'Comment', 'PostLikes', 'CommentLikes', 'User']
