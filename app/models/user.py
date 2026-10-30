"""Модель пользователя."""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    """Пользователь системы. Владелец проектов, сцен, промптов."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    projects = db.relationship("Project", back_populates="user", cascade="all, delete-orphan")
    prompts = db.relationship("Prompt", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        """Хеширует пароль и сохраняет в password_hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Проверяет пароль против сохранённого хеша."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email}>"
