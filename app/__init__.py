"""Flask application factory для PromptFlow."""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

from .config import config
from .extensions import csrf, db, login_manager, migrate


def create_app(config_name=None):
    """Создаёт и настраивает экземпляр Flask-приложения.

    :param config_name: имя конфигурации (development/testing/production).
                        По умолчанию берётся из переменной окружения FLASK_ENV,
                        а если её нет — development.
    """
    # Загружаем переменные из .env (если файл есть), чтобы локальный запуск
    # работал без ручного экспорта переменных окружения.
    load_dotenv()

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Пожалуйста, войдите в систему."
    login_manager.login_message_category = "warning"

    # Импорт моделей, чтобы они зарегистрировались в метаданных SQLAlchemy
    from app.models import project, prompt, prompt_rating, prompt_version, scene, user  # noqa: F401

    # Загрузчик пользователя для Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Регистрация блюпринтов
    from app.auth import auth_bp
    from app.main import main_bp
    from app.projects import projects_bp
    from app.prompts import prompts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(prompts_bp)
    app.register_blueprint(main_bp)

    # Проверка работоспособности приложения
    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    # Обработчики ошибок
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app
