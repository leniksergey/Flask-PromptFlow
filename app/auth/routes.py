"""Маршруты авторизации: регистрация, вход, выход."""

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import auth_bp
from app.auth.forms import LoginForm, RegisterForm
from app.extensions import db
from app.models.user import User


def is_safe_next_url(target: str | None) -> bool:
    """Разрешает только относительный путь на этом сайте.

    Безопасно: ``/projects/1``. Небезопасно: ``//evil.example``,
    ``https://evil.example``, пути с обратным слэшем (браузеры могут
    трактовать ``/\\evil.example`` как protocol-relative URL).
    """
    if not target:
        return False
    if "\\" in target or "\n" in target or "\r" in target:
        return False
    return target.startswith("/") and not target.startswith("//")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Регистрация нового пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("Пользователь с таким email уже зарегистрирован.", "warning")
            return render_template("auth/register.html", form=form)

        user = User(email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Регистрация успешна. Теперь вы можете войти.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Вход в систему."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash("Неверный email или пароль.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember_me.data)
        flash("Добро пожаловать!", "success")

        next_page = request.args.get("next")
        if not is_safe_next_url(next_page):
            next_page = url_for("main.dashboard")
        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Выход из системы (только POST, защищено CSRF)."""
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("main.dashboard"))
