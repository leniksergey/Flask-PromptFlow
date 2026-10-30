"""Модель библиотеки промптов."""

from datetime import datetime, timezone

from app.extensions import db


class Prompt(db.Model):
    """Запись библиотеки промптов пользователя."""

    __tablename__ = "prompts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name = db.Column(db.String(200), nullable=False)
    purpose = db.Column(db.String(200), nullable=True)  # назначение / тип генерации
    service = db.Column(db.String(100), nullable=True)  # AI-сервис
    tags = db.Column(db.String(500), nullable=True)  # через запятую
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="prompts")
    scenes = db.relationship("Scene", back_populates="prompt")
    versions = db.relationship(
        "PromptVersion",
        back_populates="prompt",
        cascade="all, delete-orphan",
        order_by="PromptVersion.version_number",
    )

    @property
    def latest_version(self):
        """Возвращает последнюю версию промпта или None."""
        if not self.versions:
            return None
        return self.versions[-1]

    def __repr__(self):  # pragma: no cover
        return f"<Prompt {self.name}>"
