"""Тесты проектов: CRUD, изоляция данных, 404."""


def _text(response):
    return response.get_data(as_text=True)


def _login(client, user):
    client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "password123",
        },
    )


def test_create_project(client, user):
    """Создание проекта авторизованным пользователем."""
    _login(client, user)

    response = client.post(
        "/projects/new",
        data={
            "title": "Мой проект",
            "description": "Описание проекта",
            "visual_style": "Кинематографичный",
            "content_format": "vertical_video",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Проект создан" in _text(response)
    assert "Мой проект" in _text(response)


def test_edit_project(client, user, project):
    """Редактирование своего проекта."""
    _login(client, user)

    response = client.post(
        f"/projects/{project.id}/edit",
        data={
            "title": "Обновлённый проект",
            "description": "Новое описание",
            "visual_style": "Минимализм",
            "content_format": "horizontal_video",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Проект обновлён" in _text(response)
    assert "Обновлённый проект" in _text(response)


def test_delete_project(client, user, project):
    """Удаление своего проекта."""
    _login(client, user)

    response = client.post(f"/projects/{project.id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert "Проект удалён" in _text(response)


def test_cannot_access_another_users_project(client, another_user, project):
    """Пользователь A не может открыть проект пользователя B (404)."""
    _login(client, another_user)

    response = client.get(f"/projects/{project.id}", follow_redirects=True)
    assert response.status_code == 404


def test_cannot_edit_another_users_project(client, another_user, project):
    """Пользователь A не может редактировать проект пользователя B (404)."""
    _login(client, another_user)

    response = client.post(
        f"/projects/{project.id}/edit",
        data={
            "title": "Hacked",
        },
        follow_redirects=True,
    )
    assert response.status_code == 404


def test_cannot_delete_another_users_project(client, another_user, project):
    """Пользователь A не может удалить проект пользователя B (404)."""
    _login(client, another_user)

    response = client.post(f"/projects/{project.id}/delete", follow_redirects=True)
    assert response.status_code == 404


def test_nonexistent_project_404(client, user):
    """Запрос несуществующего проекта возвращает 404."""
    _login(client, user)

    response = client.get("/projects/99999", follow_redirects=True)
    assert response.status_code == 404


def test_projects_list_requires_login(client):
    """Список проектов недоступен без входа."""
    response = client.get("/projects/", follow_redirects=False)
    assert response.status_code == 302
