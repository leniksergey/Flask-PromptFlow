"""Тесты сцен: CRUD, уникальность order, изоляция, статусы."""


def _text(response):
    return response.get_data(as_text=True)


def test_create_scene(client, user, project):
    """Создание сцены в своём проекте."""
    client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "password123",
        },
    )

    response = client.post(
        f"/projects/{project.id}/scenes/new",
        data={
            "order": 1,
            "title": "Первая сцена",
            "description": "Описание сцены",
            "duration_seconds": 30,
            "status": "planned",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Сцена добавлена" in _text(response)
    assert "Первая сцена" in _text(response)


def test_edit_scene(client, user, project, scene):
    """Редактирование своей сцены."""
    client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "password123",
        },
    )

    response = client.post(
        f"/projects/{project.id}/scenes/{scene.id}/edit",
        data={
            "order": 1,
            "title": "Обновлённая сцена",
            "description": "Новое описание",
            "duration_seconds": 60,
            "status": "in_progress",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Сцена обновлена" in _text(response)
    assert "Обновлённая сцена" in _text(response)


def test_unique_order_in_project(client, user, project, scene, app):
    """Порядок сцен уникален в рамках проекта — дубликат не создаётся."""
    client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "password123",
        },
    )

    # Создаём вторую сцену с тем же order
    response = client.post(
        f"/projects/{project.id}/scenes/new",
        data={
            "order": scene.order,
            "title": "Дублирующая сцена",
            "description": "Попытка дублирования order",
            "status": "planned",
        },
        follow_redirects=True,
    )

    # Форма должна быть повторно отображена (не редирект)
    assert response.status_code == 200
    # Проверяем, что дубликат сцены не создан
    with app.app_context():
        from app.models.scene import Scene

        scenes = Scene.query.filter_by(project_id=project.id, order=scene.order).all()
        assert len(scenes) == 1


def test_cannot_access_another_users_scene(client, another_user, project, scene):
    """Нельзя редактировать сцену чужого проекта."""
    client.post(
        "/auth/login",
        data={
            "email": another_user.email,
            "password": "password123",
        },
    )

    response = client.post(
        f"/projects/{project.id}/scenes/{scene.id}/edit",
        data={
            "order": 1,
            "title": "Hacked",
            "status": "done",
        },
        follow_redirects=True,
    )
    assert response.status_code == 404


def test_valid_statuses(client, user, project):
    """Статус сцены из допустимого набора."""
    client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "password123",
        },
    )

    for status in ("planned", "in_progress", "done"):
        response = client.post(
            f"/projects/{project.id}/scenes/new",
            data={
                "order": 10 + len(status),
                "title": f"Сцена {status}",
                "status": status,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "Сцена добавлена" in _text(response)


def test_create_scene_with_own_prompt(client, user, project, prompt, app):
    """Сцену можно связать со своим промптом."""
    client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "password123",
        },
    )

    response = client.post(
        f"/projects/{project.id}/scenes/new",
        data={
            "order": 1,
            "title": "Сцена с промптом",
            "status": "planned",
            "prompt_id": prompt.id,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Сцена добавлена" in _text(response)
    with app.app_context():
        from app.models.scene import Scene

        scene = Scene.query.filter_by(project_id=project.id, title="Сцена с промптом").one()
        assert scene.prompt_id == prompt.id


def test_cannot_link_another_users_prompt(client, user, project, another_user, app):
    """Чужой промпт нельзя привязать к сцене."""
    from tests.conftest import create_prompt

    client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "password123",
        },
    )

    with app.app_context():
        foreign = create_prompt(app.extensions["sqlalchemy"].session, another_user, name="Чужой")
        foreign_id = foreign.id

    response = client.post(
        f"/projects/{project.id}/scenes/new",
        data={
            "order": 1,
            "title": "Попытка чужого промпта",
            "status": "planned",
            "prompt_id": foreign_id,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Сцена добавлена" not in _text(response)
    with app.app_context():
        from app.models.scene import Scene

        assert Scene.query.filter_by(project_id=project.id).count() == 0


def test_delete_scene(client, user, project, scene):
    """Удаление своей сцены."""
    client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "password123",
        },
    )

    response = client.post(
        f"/projects/{project.id}/scenes/{scene.id}/delete",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Сцена удалена" in _text(response)
