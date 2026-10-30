"""Формы проектов."""

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.models.prompt import Prompt


def _coerce_optional_int(value):
    """Пустое значение в SelectField превращает в None, иначе в int."""
    if value is None or value == "":
        return None
    return int(value)


class ProjectForm(FlaskForm):
    """Форма создания и редактирования проекта."""

    title = StringField(
        "Название",
        validators=[
            DataRequired(message="Введите название проекта"),
            Length(max=200, message="Название не должно превышать 200 символов"),
        ],
    )
    description = TextAreaField("Описание / идея", validators=[Optional()])
    visual_style = StringField(
        "Визуальный стиль",
        validators=[
            Optional(),
            Length(max=200, message="Стиль не должен превышать 200 символов"),
        ],
    )
    content_format = SelectField(
        "Формат контента",
        choices=[
            ("vertical_video", "Вертикальное видео"),
            ("horizontal_video", "Горизонтальное видео"),
            ("image", "Изображение"),
        ],
        validators=[Optional()],
    )
    submit = SubmitField("Сохранить")


class SceneForm(FlaskForm):
    """Форма создания и редактирования сцены."""

    order = IntegerField(
        "Порядок",
        validators=[DataRequired(message="Введите порядковый номер")],
    )
    title = StringField(
        "Название",
        validators=[
            DataRequired(message="Введите название сцены"),
            Length(max=200, message="Название не должно превышать 200 символов"),
        ],
    )
    description = TextAreaField("Описание действия / кадра", validators=[Optional()])
    duration_seconds = IntegerField(
        "Длительность (секунды)",
        validators=[
            Optional(),
            NumberRange(min=0, message="Длительность не может быть отрицательной"),
        ],
    )
    status = SelectField(
        "Статус",
        choices=[
            ("planned", "Запланировано"),
            ("in_progress", "В работе"),
            ("done", "Готово"),
        ],
        validators=[DataRequired(message="Выберите статус")],
    )
    prompt_id = SelectField(
        "Промпт",
        coerce=_coerce_optional_int,
        validators=[Optional()],
    )
    submit = SubmitField("Сохранить")

    def populate_prompt_choices(self, user_id=None):
        """Подставляет в список только промпты текущего пользователя."""
        if user_id is None:
            user_id = current_user.id
        prompts = Prompt.query.filter_by(user_id=user_id).order_by(Prompt.name).all()
        self.prompt_id.choices = [("", "— не выбран —")] + [(p.id, p.name) for p in prompts]
