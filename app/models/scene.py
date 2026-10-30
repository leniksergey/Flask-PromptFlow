"""Модель сцены."""

from datetime import datetime, timezone

from app.extensions import db

VALID_STATUSES = ("planned", "in_progress", "done")


class Scene(db.Model):
    """Сцена конкретного проекта."""

    __tablename__ = "scenes"
    __table_args__ = (
        db.UniqueConstraint("project_id", "order", name="uq_project_order"),
        db.CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds >= 0",
            name="ck_scene_duration_non_negative",
        ),
        db.CheckConstraint(
            "status IN ('planned', 'in_progress', 'done')",
            name="ck_scene_status_valid",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    prompt_id = db.Column(
        db.Integer,
        db.ForeignKey("prompts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    status = db.Column(
        db.String(20), nullable=False, default="planned"
    )  # planned / in_progress / done
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    project = db.relationship("Project", back_populates="scenes")
    prompt = db.relationship("Prompt", back_populates="scenes")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Scene {self.order}: {self.title}>"
