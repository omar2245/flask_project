from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

from . import db


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(), nullable=False)

    user = db.relationship('User', backref='posts')
    comments = db.relationship('Comment', backref='post', cascade='all, delete', lazy=True)
    likes = db.relationship('PostLikes', backref='post', cascade='all, delete', lazy=True)

    excerpt_length = 100

    # 定義python取值
    @hybrid_property
    def content_excerpt(self):
        return self.content[:self.excerpt_length]

    # 定義sql表達
    @content_excerpt.expression
    def content_excerpt(self):
        return func.substring(self.content, 1, self.excerpt_length)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(), nullable=False)
    
    user = db.relationship('User', backref='comment')
    likes = db.relationship('CommentLikes', backref='comment', cascade='all, delete', lazy=True)


class PostLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    user = db.relationship('User', backref='post_likes')
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='post_like'),)


class CommentLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)

    user = db.relationship('User', backref='comment_likes')
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='comment_like'),)
