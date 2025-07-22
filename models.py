from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint
from flask_login import UserMixin
from config import db, app


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    __table_args__ = (
        CheckConstraint("nickname !~ '[[:punct:]]'", name='check_nickname_no_punctuation'),
    )

    def __init__(self, nickname):
        self.nickname = nickname

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.String(300), nullable=False)  # Текст комментария, до 300 символов
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Дата и время создания

    user = db.relationship('User', backref='comments')

    def __repr__(self):
        return f'<Comment {self.id} от {self.user_nickname}>'


with app.app_context():
    db.create_all()
