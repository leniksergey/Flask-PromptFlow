"""Тесты экспорта проекта и аналитики дашборда."""

import json


def _login(client, user):
    client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "password123",
        },
    )


def test_export_json(client, user, project, scene, prompt, prompt_version):
    """Экспорт проекта в JSON возвращает корректную структуру."""
    _login(client, user)

    response = client.get(f"/projects/{project.id}/export/json")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")

    data = json.loads(response.get_data(as_text=True))
    assert data["project"]["id"] == project.id
    assert data["project"]["title"] == project.title
    assert len(data["scenes"]) == 1
    assert data["scenes"][0]["title"] == scene.title
    assert data["scenes"][0]["prompt_id"] is None
    # Промпт в библиотеке есть, но не привязан к сцене — в экспорт не попадает.
    assert data["prompts"] == []


def test_export_markdown(client, user, project, scene, prompt, prompt_version):
    """Экспорт проекта в Markdown возвращает читаемый документ."""
    _login(client, user)

    response = client.get(f"/projects/{project.id}/export/markdown")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/markdown")

    content = response.get_data(as_text=True)
    assert f"# {project.title}" in content
    assert project.title in content
    assert scene.title in content
    assert prompt.name not in content
    assert prompt_version.prompt_text not in content
    assert "Промптов нет." in content


def test_export_empty_project(client, user, app):
    """Экспорт пустого проекта (без сцен и промптов) не ломается."""
    _login(client, user)

    # Создаём пустой проект
    from app.extensions import db
    from app.models.project import Project

    with app.app_context():
        empty_project = Project(user_id=user.id, title="Empty Project")
        db.session.add(empty_project)
        db.session.commit()
        project_id = empty_project.id

    response = client.get(f"/projects/{project_id}/export/json")
    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    assert data["project"]["title"] == "Empty Project"
    assert data["scenes"] == []
    assert data["prompts"] == []

    response = client.get(f"/projects/{project_id}/export/markdown")
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert "# Empty Project" in content
    assert "Сцен нет." in content
    assert "Промптов нет." in content


def test_export_includes_only_linked_prompts(
    client, user, project, scene, prompt, prompt_version, app
):
    """В экспорт попадают только промпты, привязанные к сценам проекта."""
    from tests.conftest import create_prompt, create_prompt_version

    _login(client, user)

    with app.app_context():
        unused = create_prompt(app.extensions["sqlalchemy"].session, user, name="Unused Prompt")
        create_prompt_version(app.extensions["sqlalchemy"].session, unused)
        scene.prompt_id = prompt.id
        app.extensions["sqlalchemy"].session.commit()
        unused_name = unused.name

    response = client.get(f"/projects/{project.id}/export/json")
    data = json.loads(response.get_data(as_text=True))
    assert data["scenes"][0]["prompt_id"] == prompt.id
    assert len(data["prompts"]) == 1
    assert data["prompts"][0]["title"] == prompt.name
    assert data["prompts"][0]["id"] == prompt.id
    assert len(data["prompts"][0]["versions"]) == 1
    assert unused_name not in [item["title"] for item in data["prompts"]]

    content = client.get(f"/projects/{project.id}/export/markdown").get_data(as_text=True)
    assert prompt.name in content
    assert prompt_version.prompt_text in content
    assert unused_name not in content


def test_export_requires_login(client, project):
    """Экспорт недоступен без входа."""
    response = client.get(f"/projects/{project.id}/export/json", follow_redirects=False)
    assert response.status_code == 302

    response = client.get(f"/projects/{project.id}/export/markdown", follow_redirects=False)
    assert response.status_code == 302


def test_export_cannot_access_another_users_project(client, another_user, project):
    """Пользователь A не может экспортировать проект пользователя B (404)."""
    _login(client, another_user)

    response = client.get(f"/projects/{project.id}/export/json", follow_redirects=True)
    assert response.status_code == 404

    response = client.get(f"/projects/{project.id}/export/markdown", follow_redirects=True)
    assert response.status_code == 404


def test_dashboard_shows_analytics(
    client, user, project, scene, prompt, prompt_version, prompt_rating, app
):
    """Дашборд показывает базовую аналитику."""
    _login(client, user)

    response = client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200
    content = response.get_data(as_text=True)

    assert "Проектов" in content
    assert "Сцен" in content
    assert "Промптов" in content
    assert "Версий промптов" in content
