"""Общие расширения Flask: база данных, миграции, авторизация, CSRF-защита."""

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

# Расширение login_manager будет настроено в create_app после создания приложения.
