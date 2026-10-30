"""Маршруты главной страницы / дашборда."""

from flask import redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.main import main_bp
from app.models.project import Project
from app.models.prompt import Prompt
from app.models.prompt_rating import PromptRating
from app.models.prompt_version import PromptVersion
from app.models.scene import Scene


@main_bp.route("/")
def index():
    """Главная страница: приветствие для анонима, дашборд для пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Дашборд пользователя: базовая статистика по проектам, сценам, промптам."""
    user_id = current_user.id

    projects_count = db.session.query(Project).filter_by(user_id=user_id).count()
    scenes_count = (
        db.session.query(Scene)
        .join(Project, Scene.project_id == Project.id)
        .filter(Project.user_id == user_id)
        .count()
    )
    prompts_count = db.session.query(Prompt).filter_by(user_id=user_id).count()
    versions_count = (
        db.session.query(PromptVersion)
        .join(Prompt, PromptVersion.prompt_id == Prompt.id)
        .filter(Prompt.user_id == user_id)
        .count()
    )

    # Средняя оценка по всем версиям пользователя
    avg_rating = (
        db.session.query(func.avg(PromptRating.score))
        .join(PromptVersion, PromptRating.version_id == PromptVersion.id)
        .join(Prompt, PromptVersion.prompt_id == Prompt.id)
        .filter(Prompt.user_id == user_id)
        .scalar()
    )

    # Топ-3 наиболее высоко оценённых версии
    top_versions = (
        db.session.query(
            PromptVersion,
            func.avg(PromptRating.score).label("avg_score"),
        )
        .join(PromptRating, PromptRating.version_id == PromptVersion.id)
        .join(Prompt, PromptVersion.prompt_id == Prompt.id)
        .filter(Prompt.user_id == user_id)
        .group_by(PromptVersion.id)
        .order_by(func.avg(PromptRating.score).desc())
        .limit(3)
        .all()
    )

    return render_template(
        "dashboard.html",
        projects_count=projects_count,
        scenes_count=scenes_count,
        prompts_count=prompts_count,
        versions_count=versions_count,
        avg_rating=avg_rating,
        top_versions=top_versions,
    )
