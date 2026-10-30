"""Модель оценки версии промпта."""

from datetime import datetime, timezone

from app.extensions import db


class PromptRating(db.Model):
    """Оценка версии промпта пользователем (шкала 1–5)."""

    __tablename__ = "prompt_ratings"

    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(
        db.Integer,
        db.ForeignKey("prompt_versions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    score = db.Column(db.Integer, nullable=False)  # 1–5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    version = db.relationship("PromptVersion", back_populates="ratings")

    __table_args__ = (
        db.UniqueConstraint("version_id", "user_id", name="uq_version_user_rating"),
        db.CheckConstraint("score >= 1 AND score <= 5", name="ck_rating_score_range"),
    )

    def __repr__(self):  # pragma: no cover
        return f"<PromptRating {self.version_id}:{self.user_id}={self.score}>"
