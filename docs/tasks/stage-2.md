1. # Этап 2 — Модели и проекты

> Перед началом прочитай `AGENTS.md` полностью и `docs/tasks/stage-1.md`,
> чтобы понять, что уже реализовано. Не дублируй существующий код.

## Предусловия
- Этап 1 завершён: application factory, extensions, `/health`, миграции, 
  тесты, Docker, CI работают.
- Проверь `git log` и текущую структуру — возможно, часть работы уже сделана.

## Цель этапа
Реализовать модели `User`, `Project`, `Scene`, миграции, CRUD проектов и
сцен, проверку владения данными, регистрацию/вход/выход.

## Задачи

### 1. Модель User и авторизация
- `app/models/user.py`:
  - поля: `id`, `email` (unique, index, не пустой), `password_hash`,
    `created_at`;
  - методы: `set_password`, `check_password` (через
    `werkzeug.security`);
  - связь `projects` (one-to-many, cascade delete-orphan).
- `UserMixin` от Flask-Login.
- `app/auth/routes.py` + `app/auth/forms.py`:
  - `/register` (GET/POST): email, пароль, подтверждение пароля;
  - `/login` (GET/POST): email, пароль, `remember_me`;
  - `/logout` (POST, CSRF-защищённый).
- Шаблоны: `templates/auth/register.html`, `login.html`.
- `login_manager.user_loader` в `app/extensions.py` или `app/auth/__init__.py`.
- Декоратор `@login_required` на приватных маршрутах.
- Редирект неавторизованных на `/login` с `next`-параметром.

### 2. Модель Project
- `app/models/project.py`:
  - поля: `id`, `user_id` (FK на users, `ondelete="CASCADE"`),
    `title` (не пустой, ≤ 200 символов), `description` (Text),
    `visual_style` (≤ 200), `content_format` (≤ 50, например
    `vertical_video` / `horizontal_video` / `image`),
    `created_at`, `updated_at` (auto-update);
  - связь `scenes` (one-to-many, cascade delete-orphan, order_by
    `Scene.order`);
  - связь `user` (back_populates).
- Индекс на `user_id`.

### 3. Модель Scene
- `app/models/scene.py`:
  - поля: `id`, `project_id` (FK, `ondelete="CASCADE"`),
    `order` (Integer, не пустой), `title` (≤ 200), `description`
    (Text), `duration_seconds` (Integer, ≥ 0, nullable),
    `status` (enum/строка: `planned`, `in_progress`, `done`,
    default `planned`), `created_at`, `updated_at`;
  - `UniqueConstraint("project_id", "order")` — уникальный порядок
    сцен в проекте;
  - индекс на `project_id`.
- Порядок сцен: при создании/удалении/переупорядочивании поддерживай
  последовательность без дыр или явно документируй допущение.

### 4. Миграции
- Создать миграцию: `flask db migrate -m "add user, project, scene"`.
- Проверить `flask db upgrade` и `flask db downgrade` (пустая БД →
  upgrade → downgrade → upgrade).

### 5. CRUD проектов
- `app/projects/routes.py` + `app/projects/forms.py`:
  - `GET /projects/` — список проектов текущего пользователя;
  - `GET/POST /projects/new` — создание;
  - `GET /projects/<int:id>` — просмотр (только владелец);
  - `GET/POST /projects/<int:id>/edit` — редактирование;
  - `POST /projects/<int:id>/delete` — удаление (CSRF, только
    владелец).
- **Проверка владения на сервере**: любая попытка открыть чужой
  проект → 404 (не 403, чтобы не раскрывать существование).
- Шаблоны: `templates/projects/list.html`, `detail.html`, `form.html`.

### 6. CRUD сцен
- Маршруты внутри проекта:
  - `GET/POST /projects/<int:id>/scenes/new`;
  - `GET/POST /projects/<int:pid>/scenes/<int:sid>/edit`;
  - `POST /projects/<int:pid>/scenes/<int:sid>/delete`;
  - `POST /projects/<int:id>/scenes/reorder` (принимает JSON/форму с
    порядком).
- Проверка, что сцена принадлежит проекту, а проект — пользователю.
- Валидация: `order` уникален в рамках проекта, `duration_seconds` ≥ 0,
  `status` из допустимого набора.

### 7. Главная страница
- `app/templates/dashboard.html` или `index.html`:
  - для анонимного — приветствие + ссылки на login/register;
  - для авторизованного — количество проектов, ссылка на список.
- Полная аналитика — на Этапе 4, сейчас только базовая.

### 8. Обработка ошибок
- Страницы 403/404/500 (`templates/errors/`).
- В production не показывать traceback (проверить `DEBUG=False`).

### 9. Тесты
Файлы:
- `tests/test_auth.py`:
  - регистрация успешна;
  - повторная регистрация с тем же email — ошибка;
  - корректный вход/выход;
  - неверный пароль — отказ;
  - приватная страница недоступна анонимному.
- `tests/test_projects.py`:
  - создание/редактирование/удаление проекта;
  - пользователь A не может открыть/изменить/удалить проект B
    (ожидается 404);
  - отсутствующий id → 404.
- `tests/test_scenes.py`:
  - создание/редактирование сцены;
  - уникальность `order` в проекте;
  - нельзя менять сцену чужого проекта;
  - корректные статусы.
Все тесты используют фикстуры из `conftest.py`; добавь фабрики
пользователя/проекта/сцены, чтобы не дублировать код.

### 10. Документация
- Обновить README: разделы про регистрацию, вход, проекты, сцены.
- Указать команды миграций.

## Проверки перед завершением
```bash
pytest -q
ruff check .
ruff format --check .
flask db upgrade
git diff