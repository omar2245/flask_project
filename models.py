import pytz
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
tz = pytz.timezone('Asia/Taipei')

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255),  nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz))