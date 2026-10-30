"""Тесты библиотеки промптов: версии, оценки, поиск, изоляция."""


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


def test_create_prompt(client, user, app):
    """Создание промпта с первой версией."""
    _login(client, user)
    response = client.post(
        "/prompts/new",
        data={
            "name": "Тестовый промпт",
            "purpose": "Генерация видео",
            "service": "Runway",
            "tags": "видео, ютуб",
            "prompt_text": "Кинографичный кадр города",
            "negative_prompt": "размытый, низкое качество",
            "change_note": "Первый черновик",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Промпт создан" in _text(response)
    assert "Тестовый промпт" in _text(response)

    with app.app_context():
        from app.models.prompt import Prompt
        from app.models.prompt_version import PromptVersion

        prompt = Prompt.query.filter_by(name="Тестовый промпт").first()
        assert prompt is not None
        assert prompt.user_id == user.id
        assert prompt.tags == "видео, ютуб"
        versions = PromptVersion.query.filter_by(prompt_id=prompt.id).all()
        assert len(versions) == 1
        assert versions[0].version_number == 1
        assert versions[0].prompt_text == "Кинографичный кадр города"


def test_create_duplicate_version(client, user, prompt, prompt_version, app):
    """Редактирование промпта создаёт новую версию, а не перезаписывает старую."""
    _login(client, user)
    response = client.post(
        f"/prompts/{prompt.id}/edit",
        data={
            "name": prompt.name,
            "purpose": prompt.purpose,
            "service": prompt.service,
            "tags": prompt.tags or "",
            "prompt_text": "Обновлённый текст промпта",
            "negative_prompt": "",
            "change_note": "Обновление после теста",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Версия 2 сохранена" in _text(response)

    with app.app_context():
        from app.models.prompt_version import PromptVersion

        versions = PromptVersion.query.filter_by(prompt_id=prompt.id).all()
        assert len(versions) == 2
        assert versions[0].version_number == 1
        assert versions[1].version_number == 2
        assert versions[1].prompt_text == "Обновлённый текст промпта"
        # старая версия остаётся доступной
        assert versions[0].prompt_text == prompt_version.prompt_text


def test_prompt_detail_shows_versions(client, user, prompt, prompt_version):
    """На странице промпта показаны его версии."""
    _login(client, user)
    response = client.get(f"/prompts/{prompt.id}", follow_redirects=True)
    assert response.status_code == 200
    text = _text(response)
    assert prompt.name in text
    assert f"v{prompt_version.version_number}" in text


def test_version_detail(client, user, prompt, prompt_version):
    """На странице версии показан текст промпта."""
    _login(client, user)
    response = client.get(
        f"/prompts/{prompt.id}/versions/{prompt_version.id}",
        follow_redirects=True,
    )
    assert response.status_code == 200
    text = _text(response)
    assert prompt_version.prompt_text in text


def test_cannot_access_another_users_prompt(client, another_user, prompt):
    """Пользователь A не может открыть промпт пользователя B (404)."""
    _login(client, another_user)
    response = client.get(f"/prompts/{prompt.id}", follow_redirects=True)
    assert response.status_code == 404


def test_delete_prompt(client, user, prompt, app):
    """Удаление промпта удаляет его версии и оценки каскадно."""
    _login(client, user)
    response = client.post(f"/prompts/{prompt.id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert "Промпт удалён" in _text(response)

    with app.app_context():
        from app.extensions import db
        from app.models.prompt import Prompt

        assert db.session.get(Prompt, prompt.id) is None


def test_rate_version(client, user, prompt, prompt_version, app):
    """Оценка версии промпта (1–5) с комментарием."""
    _login(client, user)
    response = client.post(
        f"/prompts/{prompt.id}/versions/{prompt_version.id}/rate",
        data={
            "score": "5",
            "comment": "Отличный результат",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Оценка сохранена" in _text(response)

    with app.app_context():
        from app.models.prompt_rating import PromptRating

        rating = PromptRating.query.filter_by(version_id=prompt_version.id, user_id=user.id).first()
        assert rating is not None
        assert rating.score == 5
        assert rating.comment == "Отличный результат"


def test_update_rating(client, user, prompt, prompt_version):
    """Повторная оценка обновляет существующую запись, а не создаёт дубль."""
    _login(client, user)
    client.post(
        f"/prompts/{prompt.id}/versions/{prompt_version.id}/rate",
        data={
            "score": "2",
            "comment": "Не понравилось",
        },
        follow_redirects=True,
    )
    from app.models.prompt_rating import PromptRating

    ratings = PromptRating.query.filter_by(version_id=prompt_version.id, user_id=user.id).all()
    assert len(ratings) == 1
    assert ratings[0].score == 2
    assert ratings[0].comment == "Не понравилось"


def test_search_and_filter_prompts(client, user, app):
    """Поиск и фильтры по тегу и сервису возвращают только свои промпты."""
    _login(client, user)
    client.post(
        "/prompts/new",
        data={
            "name": "Видео промпт",
            "purpose": "Генерация видео",
            "service": "Runway",
            "tags": "видео, ютуб",
            "prompt_text": "Промпт 1",
            "change_note": "v1",
        },
    )
    client.post(
        "/prompts/new",
        data={
            "name": "Изображение",
            "purpose": "Генерация изображения",
            "service": "Midjourney",
            "tags": "изображение, арт",
            "prompt_text": "Промпт 2",
            "change_note": "v1",
        },
    )

    response = client.get("/prompts/?search=Видео", follow_redirects=True)
    assert response.status_code == 200
    text = _text(response)
    assert "Видео промпт" in text
    assert "Изображение" not in text

    response = client.get("/prompts/?tag=арт", follow_redirects=True)
    assert response.status_code == 200
    text = _text(response)
    assert "Изображение" in text
    assert "Видео промпт" not in text

    response = client.get("/prompts/?service=Runway", follow_redirects=True)
    assert response.status_code == 200
    text = _text(response)
    assert "Видео промпт" in text
    assert "Изображение" not in text


def test_prompts_list_requires_login(client):
    """Список промптов недоступен без входа."""
    response = client.get("/prompts/", follow_redirects=False)
    assert response.status_code == 302
