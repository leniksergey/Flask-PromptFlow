"""Маршруты проектов: список, просмотр, создание, редактирование, удаление."""

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
from app.models.project import Project
from app.models.scene import Scene
from app.projects import projects_bp
from app.projects.forms import ProjectForm, SceneForm


def _get_user_project_or_404(project_id):
    """Возвращает проект текущего пользователя или 404.

    404 (а не 403) используется, чтобы не раскрывать существование чужих проектов.
    """
    project = db.session.get(Project, project_id)
    if project is None or project.user_id != current_user.id:
        abort(404)
    return project


@projects_bp.route("/")
@login_required
def list():
    """Список проектов текущего пользователя."""
    projects = (
        Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
    )
    return render_template("projects/list.html", projects=projects)


@projects_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    """Создание нового проекта."""
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            visual_style=form.visual_style.data,
            content_format=form.content_format.data,
        )
        db.session.add(project)
        db.session.commit()
        flash("Проект создан.", "success")
        return redirect(url_for("projects.detail", id=project.id))
    return render_template("projects/form.html", form=form, action="create")


@projects_bp.route("/<int:id>")
@login_required
def detail(id):
    """Просмотр проекта со списком сцен."""
    project = _get_user_project_or_404(id)
    return render_template("projects/detail.html", project=project)


@projects_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    """Редактирование проекта."""
    project = _get_user_project_or_404(id)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.visual_style = form.visual_style.data
        project.content_format = form.content_format.data
        db.session.commit()
        flash("Проект обновлён.", "success")
        return redirect(url_for("projects.detail", id=project.id))
    return render_template("projects/form.html", form=form, action="edit", project=project)


@projects_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    """Удаление проекта (с каскадным удалением сцен)."""
    project = _get_user_project_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash("Проект удалён.", "success")
    return redirect(url_for("projects.list"))


@projects_bp.route("/<int:project_id>/scenes/new", methods=["GET", "POST"])
@login_required
def scene_new(project_id):
    """Создание сцены в проекте."""
    project = _get_user_project_or_404(project_id)

    max_order = (
        db.session.query(db.func.max(Scene.order)).filter_by(project_id=project_id).scalar() or 0
    )

    form = SceneForm()
    form.populate_prompt_choices()
    form.order.data = max_order + 1
    if form.validate_on_submit():
        scene = Scene(
            project_id=project_id,
            order=form.order.data,
            title=form.title.data,
            description=form.description.data,
            duration_seconds=form.duration_seconds.data,
            status=form.status.data,
            prompt_id=form.prompt_id.data,
        )
        db.session.add(scene)
        db.session.commit()
        flash("Сцена добавлена.", "success")
        return redirect(url_for("projects.detail", id=project_id))
    return render_template("projects/scene_form.html", form=form, project=project, action="create")


@projects_bp.route("/<int:project_id>/scenes/<int:scene_id>/edit", methods=["GET", "POST"])
@login_required
def scene_edit(project_id, scene_id):
    """Редактирование сцены."""
    project = _get_user_project_or_404(project_id)
    scene = db.session.get(Scene, scene_id)
    if scene is None or scene.project_id != project.id:
        abort(404)

    form = SceneForm(obj=scene)
    form.populate_prompt_choices()
    if form.validate_on_submit():
        new_order = form.order.data
        if new_order != scene.order:
            existing = Scene.query.filter_by(project_id=project_id, order=new_order).first()
            if existing:
                flash(
                    f"Порядок {new_order} уже занят другой сценой в этом проекте.",
                    "danger",
                )
                return render_template(
                    "projects/scene_form.html",
                    form=form,
                    project=project,
                    action="edit",
                )
        scene.order = new_order
        scene.title = form.title.data
        scene.description = form.description.data
        scene.duration_seconds = form.duration_seconds.data
        scene.status = form.status.data
        scene.prompt_id = form.prompt_id.data
        db.session.commit()
        flash("Сцена обновлена.", "success")
        return redirect(url_for("projects.detail", id=project_id))
    return render_template(
        "projects/scene_form.html",
        form=form,
        project=project,
        action="edit",
    )


@projects_bp.route("/<int:project_id>/scenes/<int:scene_id>/delete", methods=["POST"])
@login_required
def scene_delete(project_id, scene_id):
    """Удаление сцены."""
    project = _get_user_project_or_404(project_id)
    scene = db.session.get(Scene, scene_id)
    if scene is None or scene.project_id != project.id:
        abort(404)

    db.session.delete(scene)
    db.session.commit()

    # Закрываем дырки в порядке после удаления
    _reorder_scenes(project_id)

    flash("Сцена удалена.", "success")
    return redirect(url_for("projects.detail", id=project_id))


@projects_bp.route("/<int:project_id>/scenes/reorder", methods=["POST"])
@login_required
def scenes_reorder(project_id):
    """Переупорядочение сцен проекта.

    Ожидает JSON вида {"scene_ids": [id1, id2, ...]} или форму с полем scene_ids.
    """
    _get_user_project_or_404(project_id)

    data = request.get_json(silent=True) or {}
    scene_ids = data.get("scene_ids")
    if scene_ids is None:
        scene_ids = request.form.getlist("scene_ids")

    if not scene_ids:
        if request.is_json:
            return {"error": "scene_ids required"}, 400
        flash("Не указан порядок сцен.", "danger")
        return redirect(url_for("projects.detail", id=project_id))

    scene_ids = [int(sid) for sid in scene_ids]
    scenes = Scene.query.filter_by(project_id=project_id).all()
    scene_by_id = {s.id: s for s in scenes}

    # Проверяем, что все сцены belong to this project
    for sid in scene_ids:
        if sid not in scene_by_id:
            abort(404)

    # Присваиваем новые порядковые номера
    for index, sid in enumerate(scene_ids, start=1):
        scene_by_id[sid].order = index

    db.session.commit()

    if request.is_json:
        return {"status": "ok"}
    flash("Порядок сцен обновлён.", "success")
    return redirect(url_for("projects.detail", id=project_id))


def _reorder_scenes(project_id):
    """Закрывает дырки в порядке сцен проекта после удаления."""
    scenes = Scene.query.filter_by(project_id=project_id).order_by(Scene.order).all()
    for index, scene in enumerate(scenes, start=1):
        scene.order = index
    db.session.commit()


@projects_bp.route("/<int:project_id>/export/json")
@login_required
def export_json(project_id):
    """Экспорт проекта в JSON (скачивание файла)."""
    from flask import make_response

    from app.services.export_service import export_project_json

    project = _get_user_project_or_404(project_id)
    data = export_project_json(project)

    import json

    response = make_response(json.dumps(data, ensure_ascii=False, indent=2))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["Content-Disposition"] = f'attachment; filename="project_{project_id}.json"'
    return response


@projects_bp.route("/<int:project_id>/export/markdown")
@login_required
def export_markdown(project_id):
    """Экспорт проекта в Markdown (скачивание файла)."""
    from flask import make_response

    from app.services.export_service import export_project_markdown

    project = _get_user_project_or_404(project_id)
    content = export_project_markdown(project)

    response = make_response(content)
    response.headers["Content-Type"] = "text/markdown; charset=utf-8"
    response.headers["Content-Disposition"] = f'attachment; filename="project_{project_id}.md"'
    return response
