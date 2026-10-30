"""Модель версии промпта (неизменяемый снимок)."""

from datetime import datetime, timezone

from app.extensions import db


class PromptVersion(db.Model):
    """Неизменяемая версия промпта."""

    __tablename__ = "prompt_versions"

    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(
        db.Integer,
        db.ForeignKey("prompts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    version_number = db.Column(db.Integer, nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)
    negative_prompt = db.Column(db.Text, nullable=True)
    camera_params = db.Column(db.String(500), nullable=True)
    lighting = db.Column(db.String(500), nullable=True)
    visual_style = db.Column(db.String(500), nullable=True)
    frame_format = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)  # дополнительные заметки
    change_note = db.Column(db.String(500), nullable=True)  # причина изменения
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    prompt = db.relationship("Prompt", back_populates="versions")
    ratings = db.relationship(
        "PromptRating",
        back_populates="version",
        cascade="all, delete-orphan",
    )

    __table_args__ = (db.UniqueConstraint("prompt_id", "version_number", name="uq_prompt_version"),)

    @property
    def average_rating(self):
        """Средняя оценка версии или None, если оценок нет."""
        if not self.ratings:
            return None
        return sum(r.score for r in self.ratings) / len(self.ratings)

    def __repr__(self):  # pragma: no cover
        return f"<PromptVersion {self.prompt_id}:{self.version_number}>"
