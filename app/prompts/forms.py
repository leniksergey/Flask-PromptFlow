"""Формы библиотеки промптов."""

from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional


class PromptForm(FlaskForm):
    """Форма создания и редактирования промпта."""

    name = StringField(
        "Название",
        validators=[
            DataRequired(message="Введите название промпта"),
            Length(max=200, message="Название не должно превышать 200 символов"),
        ],
    )
    purpose = StringField(
        "Назначение / тип генерации",
        validators=[
            Optional(),
            Length(max=200, message="Не более 200 символов"),
        ],
    )
    service = StringField(
        "AI-сервис",
        validators=[
            Optional(),
            Length(max=100, message="Не более 100 символов"),
        ],
    )
    tags = StringField(
        "Теги (через запятую)",
        validators=[
            Optional(),
            Length(max=500, message="Не более 500 символов"),
        ],
    )
    submit = SubmitField("Сохранить")


class PromptVersionForm(FlaskForm):
    """Форма создания новой версии промпта."""

    prompt_text = TextAreaField(
        "Текст промпта",
        validators=[DataRequired(message="Введите текст промпта")],
    )
    negative_prompt = TextAreaField("Negative prompt", validators=[Optional()])
    camera_params = StringField(
        "Параметры камеры",
        validators=[
            Optional(),
            Length(max=500, message="Не более 500 символов"),
        ],
    )
    lighting = StringField(
        "Освещение",
        validators=[
            Optional(),
            Length(max=500, message="Не более 500 символов"),
        ],
    )
    visual_style = StringField(
        "Визуальный стиль",
        validators=[
            Optional(),
            Length(max=500, message="Не более 500 символов"),
        ],
    )
    frame_format = StringField(
        "Формат кадра",
        validators=[
            Optional(),
            Length(max=100, message="Не более 100 символов"),
        ],
    )
    notes = TextAreaField("Дополнительные заметки", validators=[Optional()])
    change_note = StringField(
        "Причина изменения",
        validators=[
            Optional(),
            Length(max=500, message="Не более 500 символов"),
        ],
    )
    submit = SubmitField("Сохранить версию")


class PromptRatingForm(FlaskForm):
    """Форма оценки версии промпта."""

    score = SelectField(
        "Оценка",
        choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")],
        validators=[DataRequired(message="Выберите оценку от 1 до 5")],
    )
    comment = TextAreaField("Комментарий о результате", validators=[Optional()])
    submit = SubmitField("Оценить")
