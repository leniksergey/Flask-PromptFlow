"""Конфигурация приложения для development, testing и production.

Все секреты и строки подключения берутся только из переменных окружения.
В коде нет дефолтных секретов.
"""

import os

from sqlalchemy.pool import StaticPool


class Config:
    """Базовая конфигурация."""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    @staticmethod
    def init_app(app):
        """Проверка обязательных настроек после создания приложения."""
        if not app.config.get("SECRET_KEY"):
            raise RuntimeError("SECRET_KEY must be set in environment")
        if not app.config.get("SQLALCHEMY_DATABASE_URI"):
            raise RuntimeError("DATABASE_URL must be set in environment")


class DevelopmentConfig(Config):
    """Конфигурация для разработки."""

    DEBUG = True


class TestingConfig(Config):
    """Конфигурация для тестов. База данных — SQLite in-memory."""

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }


class ProductionConfig(Config):
    """Конфигурация для продакшена."""

    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
