"""Фикстуры и фабрики для тестов PromptFlow."""

import os

# Переменные окружения нужно задать до импорта приложения, т.к. настройки
# конфига считываются из окружения при импорте модуля app.config.
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest  # noqa: E402

from app import create_app  # noqa: E402
from app.extensions import db as _db  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.models.prompt import Prompt  # noqa: E402
from app.models.prompt_rating import PromptRating  # noqa: E402
from app.models.prompt_version import PromptVersion  # noqa: E402
from app.models.scene import Scene  # noqa: E402
from app.models.user import User  # noqa: E402


@pytest.fixture
def app():
    """Экземпляр приложения с тестовой конфигурацией и созданной БД."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    """Тестовый клиент Flask."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Объект SQLAlchemy для работы с БД в тестах."""
    return _db


# --- Фабрики ---


def create_user(session, email="user@example.com", password="password123"):
    """Создаёт и сохраняет пользователя в БД."""
    user = User(email=email)
    user.set_password(password)
    session.add(user)
    session.commit()
    return user


def create_project(session, user, title="Test Project", description=None):
    """Создаёт и сохраняет проект в БД."""
    project = Project(
        user_id=user.id,
        title=title,
        description=description,
    )
    session.add(project)
    session.commit()
    return project


def create_scene(session, project, order=1, title="Test Scene", status="planned", prompt=None):
    """Создаёт и сохраняет сцену в БД."""
    scene = Scene(
        project_id=project.id,
        order=order,
        title=title,
        status=status,
        prompt_id=prompt.id if prompt is not None else None,
    )
    session.add(scene)
    session.commit()
    return scene


@pytest.fixture
def user(db):
    """Тестовый пользователь."""
    return create_user(db.session)


@pytest.fixture
def another_user(db):
    """Второй тестовый пользователь (для проверки изоляции данных)."""
    return create_user(db.session, email="another@example.com")


@pytest.fixture
def project(db, user):
    """Тестовый проект пользователя."""
    return create_project(db.session, user)


@pytest.fixture
def scene(db, project):
    """Тестовая сцена проекта."""
    return create_scene(db.session, project)


# --- Фабрики промптов ---


def create_prompt(session, user, name="Test Prompt", purpose=None, service=None, tags=None):
    """Создаёт и сохраняет промпт в БД."""
    prompt = Prompt(
        user_id=user.id,
        name=name,
        purpose=purpose,
        service=service,
        tags=tags,
    )
    session.add(prompt)
    session.commit()
    return prompt


def create_prompt_version(
    session,
    prompt,
    version_number=1,
    prompt_text="Test prompt text",
    negative_prompt=None,
    change_note="Test version",
):
    """Создаёт и сохраняет версию промпта в БД."""
    version = PromptVersion(
        prompt_id=prompt.id,
        version_number=version_number,
        prompt_text=prompt_text,
        negative_prompt=negative_prompt,
        change_note=change_note,
    )
    session.add(version)
    session.commit()
    return version


def create_prompt_rating(session, version, user, score=4, comment=None):
    """Создаёт и сохраняет оценку версии промпта в БД."""
    rating = PromptRating(
        version_id=version.id,
        user_id=user.id,
        score=score,
        comment=comment,
    )
    session.add(rating)
    session.commit()
    return rating


@pytest.fixture
def prompt(db, user):
    """Тестовый промпт пользователя."""
    return create_prompt(db.session, user)


@pytest.fixture
def prompt_version(db, prompt):
    """Тестовая версия промпта."""
    return create_prompt_version(db.session, prompt)


@pytest.fixture
def prompt_rating(db, prompt_version, user):
    """Тестовая оценка версии промпта."""
    return create_prompt_rating(db.session, prompt_version, user)
