"""Тесты авторизации: регистрация, вход, выход."""


def _text(response):
    return response.get_data(as_text=True)


def test_register_success(client, app):
    """Регистрация нового пользователя успешна."""
    with app.app_context():
        from app.models.user import User

        response = client.post(
            "/auth/register",
            data={
                "email": "newuser@example.com",
                "password": "password123",
                "confirm_password": "password123",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        user = User.query.filter_by(email="newuser@example.com").first()
        assert user is not None
        assert user.check_password("password123")


def test_register_duplicate_email(client, user, app):
    """Повторная регистрация с тем же email не создаёт дубликата пользователя."""
    response = client.post(
        "/auth/register",
        data={
            "email": user.email,
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    # Проверяем, что в БД остался только один пользователь с таким email
    with app.app_context():
        from app.models.user import User

        users = User.query.filter_by(email=user.email).all()
        assert len(users) == 1


def test_login_success(client, user):
    """Корректный вход в систему."""
    response = client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Добро пожаловать" in _text(response)


def test_login_wrong_password(client, user):
    """Неверный пароль не даёт войти."""
    response = client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "wrongpassword",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Неверный email или пароль" in _text(response)


def test_login_logout(client, user):
    """Вход и выход из системы."""
    client.post(
        "/auth/login",
        data={
            "email": user.email,
            "password": "password123",
        },
        follow_redirects=True,
    )

    response = client.post("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert "Вы вышли" in _text(response)


def test_private_page_redirects_anonymous(client):
    """Приватная страница перенаправляет анонима на вход."""
    response = client.get("/projects/", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_is_safe_next_url():
    """Локальные пути разрешены, protocol-relative и внешние URL — нет."""
    from app.auth.routes import is_safe_next_url

    assert is_safe_next_url("/projects/")
    assert is_safe_next_url("/prompts/1")
    assert not is_safe_next_url(None)
    assert not is_safe_next_url("")
    assert not is_safe_next_url("projects/")
    assert not is_safe_next_url("//evil.example")
    assert not is_safe_next_url("https://evil.example/phish")
    assert not is_safe_next_url("/\\evil.example")


def test_login_next_allows_internal_path(client, user):
    """После входа разрешён относительный путь на этом сайте."""
    response = client.post(
        "/auth/login?next=/projects/",
        data={
            "email": user.email,
            "password": "password123",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.location == "/projects/"


def test_login_next_rejects_protocol_relative_url(client, user):
    """``//evil.example`` не должен уводить браузер на чужой хост."""
    response = client.post(
        "/auth/login?next=//evil.example",
        data={
            "email": user.email,
            "password": "password123",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "evil" not in response.location
    assert "/dashboard" in response.location


def test_login_next_rejects_absolute_url(client, user):
    """Абсолютный внешний URL после входа игнорируется."""
    response = client.post(
        "/auth/login?next=https://evil.example/phish",
        data={
            "email": user.email,
            "password": "password123",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "evil" not in response.location
    assert "/dashboard" in response.location
