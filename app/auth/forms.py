"""Формы авторизации."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    """Форма регистрации нового пользователя."""

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Введите email"),
            Email(message="Некорректный адрес email"),
            Length(max=255, message="Email слишком длинный"),
        ],
    )
    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Введите пароль"),
            Length(min=6, max=128, message="Пароль от 6 до 128 символов"),
        ],
    )
    confirm_password = PasswordField(
        "Подтверждение пароля",
        validators=[
            DataRequired(message="Подтвердите пароль"),
            EqualTo("password", message="Пароли не совпадают"),
        ],
    )
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    """Форма входа в систему."""

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Введите email"),
            Email(message="Некорректный адрес email"),
        ],
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(message="Введите пароль")],
    )
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")
