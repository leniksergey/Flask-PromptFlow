"""Маршруты библиотеки промптов: список, версии, оценки."""

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import db
from app.models.prompt import Prompt
from app.models.prompt_rating import PromptRating
from app.models.prompt_version import PromptVersion
from app.prompts import prompts_bp
from app.prompts.forms import PromptForm, PromptRatingForm, PromptVersionForm


def _get_user_prompt_or_404(prompt_id):
    """Возвращает промпт текущего пользователя или 404."""
    prompt = db.session.get(Prompt, prompt_id)
    if prompt is None or prompt.user_id != current_user.id:
        abort(404)
    return prompt


@prompts_bp.route("/")
@login_required
def list():
    """Список промптов текущего пользователя с поиском и фильтрацией."""
    query = Prompt.query.filter_by(user_id=current_user.id)

    search = (request.args.get("search") or "").strip()
    tag = (request.args.get("tag") or "").strip()
    service = (request.args.get("service") or "").strip()

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Prompt.name.ilike(like),
                Prompt.purpose.ilike(like),
                Prompt.tags.ilike(like),
            )
        )
    if tag:
        query = query.filter(Prompt.tags.ilike(f"%{tag}%"))
    if service:
        query = query.filter(Prompt.service == service)

    prompts = query.order_by(Prompt.updated_at.desc()).all()

    # Доступные теги и сервисы для фильтров (только свои данные)
    all_tags = set()
    all_services = set()
    for p in Prompt.query.filter_by(user_id=current_user.id).all():
        if p.tags:
            for t in p.tags.split(","):
                t = t.strip()
                if t:
                    all_tags.add(t)
        if p.service:
            all_services.add(p.service)

    return render_template(
        "prompts/list.html",
        prompts=prompts,
        search=search,
        tag=tag,
        service=service,
        all_tags=sorted(all_tags),
        all_services=sorted(all_services),
    )


@prompts_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    """Создание промпта с первой версией."""
    form = PromptForm()
    version_form = PromptVersionForm()
    if form.validate_on_submit() and version_form.validate_on_submit():
        prompt = Prompt(
            user_id=current_user.id,
            name=form.name.data,
            purpose=form.purpose.data,
            service=form.service.data,
            tags=form.tags.data,
        )
        db.session.add(prompt)
        db.session.flush()

        version = PromptVersion(
            prompt_id=prompt.id,
            version_number=1,
            prompt_text=version_form.prompt_text.data,
            negative_prompt=version_form.negative_prompt.data,
            camera_params=version_form.camera_params.data,
            lighting=version_form.lighting.data,
            visual_style=version_form.visual_style.data,
            frame_format=version_form.frame_format.data,
            notes=version_form.notes.data,
            change_note="Первая версия",
        )
        db.session.add(version)
        db.session.commit()

        flash("Промпт создан.", "success")
        return redirect(url_for("prompts.detail", id=prompt.id))
    return render_template(
        "prompts/form.html",
        form=form,
        version_form=version_form,
        action="create",
    )


@prompts_bp.route("/<int:id>")
@login_required
def detail(id):
    """Просмотр промпта со списком версий."""
    prompt = _get_user_prompt_or_404(id)
    return render_template("prompts/detail.html", prompt=prompt)


@prompts_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    """Редактирование промпта — создаёт новую версию."""
    prompt = _get_user_prompt_or_404(id)

    latest = prompt.latest_version
    form = PromptForm(obj=prompt)
    version_form = PromptVersionForm(obj=latest) if latest else PromptVersionForm()

    if form.validate_on_submit() and version_form.validate_on_submit():
        prompt.name = form.name.data
        prompt.purpose = form.purpose.data
        prompt.service = form.service.data
        prompt.tags = form.tags.data

        version_number = (latest.version_number if latest else 0) + 1
        version = PromptVersion(
            prompt_id=prompt.id,
            version_number=version_number,
            prompt_text=version_form.prompt_text.data,
            negative_prompt=version_form.negative_prompt.data,
            camera_params=version_form.camera_params.data,
            lighting=version_form.lighting.data,
            visual_style=version_form.visual_style.data,
            frame_format=version_form.frame_format.data,
            notes=version_form.notes.data,
            change_note=version_form.change_note.data,
        )
        db.session.add(version)
        db.session.commit()

        flash(f"Версия {version_number} сохранена.", "success")
        return redirect(url_for("prompts.detail", id=prompt.id))

    return render_template(
        "prompts/form.html",
        form=form,
        version_form=version_form,
        action="edit",
        prompt=prompt,
    )


@prompts_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    """Удаление промпта со всеми версиями и оценками."""
    prompt = _get_user_prompt_or_404(id)
    db.session.delete(prompt)
    db.session.commit()
    flash("Промпт удалён.", "success")
    return redirect(url_for("prompts.list"))


@prompts_bp.route("/<int:prompt_id>/versions/<int:version_id>")
@login_required
def version_detail(prompt_id, version_id):
    """Просмотр конкретной версии промпта."""
    prompt = _get_user_prompt_or_404(prompt_id)
    version = db.session.get(PromptVersion, version_id)
    if version is None or version.prompt_id != prompt.id:
        abort(404)

    user_rating = None
    if current_user.is_authenticated:
        user_rating = PromptRating.query.filter_by(
            version_id=version.id, user_id=current_user.id
        ).first()

    rating_form = PromptRatingForm()

    return render_template(
        "prompts/version_detail.html",
        prompt=prompt,
        version=version,
        user_rating=user_rating,
        form=rating_form,
    )


@prompts_bp.route("/<int:prompt_id>/versions/<int:version_id>/rate", methods=["POST"])
@login_required
def rate_version(prompt_id, version_id):
    """Оценка версии промпта (1–5) с комментарием."""
    prompt = _get_user_prompt_or_404(prompt_id)
    version = db.session.get(PromptVersion, version_id)
    if version is None or version.prompt_id != prompt.id:
        abort(404)

    form = PromptRatingForm()
    if form.validate_on_submit():
        existing = PromptRating.query.filter_by(
            version_id=version.id, user_id=current_user.id
        ).first()
        if existing:
            existing.score = int(form.score.data)
            existing.comment = form.comment.data
        else:
            rating = PromptRating(
                version_id=version.id,
                user_id=current_user.id,
                score=int(form.score.data),
                comment=form.comment.data,
            )
            db.session.add(rating)
        db.session.commit()
        flash("Оценка сохранена.", "success")
        return redirect(
            url_for(
                "prompts.version_detail",
                prompt_id=prompt_id,
                version_id=version_id,
            )
        )

    return redirect(
        url_for(
            "prompts.version_detail",
            prompt_id=prompt_id,
            version_id=version_id,
        )
    )
