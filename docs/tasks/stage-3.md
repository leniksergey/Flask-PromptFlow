# Этап 3 — Промпты, версии, оценки

> Перед началом прочитай `AGENTS.md` полностью, `stage-1.md` и `stage-2.md`. Проверь, что модели User/Project/Scene и авторизация готовы. Не дублируй существующее.

## Цель этапа
Реализовать библиотеку промптов, версионирование, оценки, теги и базовый поиск.

## Задачи

### 1. Модель Prompt
- `app/models/prompt.py`:
  - поля: `id`, `user_id` (FK, cascade), `title` (≤ 200, не пустой), `purpose` (≤ 100, назначение/тип генерации), `ai_service` (≤ 100, nullable — обычные данные, не enum), `tags` (≤ 500, строка через запятую либо связь с отдельной таблицей — выбери простое решение и задокументируй), `created_at`, `updated_at`;
  - связи: `user`, `versions` (one-to-many, cascade delete-orphan, order_by `version_number`).
- Индекс на `user_id`.

### 2. Модель PromptVersion
- `app/models/prompt_version.py`:
  - поля: `id`, `prompt_id` (FK, cascade), `version_number` (Integer, ≥ 1), `prompt_text` (Text, не пустой), `negative_prompt` (Text, nullable), `camera` (≤ 200, nullable), `lighting` (≤ 200, nullable), `style` (≤ 200, nullable), `aspect_ratio` (≤ 50, nullable), `notes` (Text, nullable), `change_note` (≤ 500, примечание об изменении), `created_at`;
  - `UniqueConstraint("prompt_id", "version_number")`;
  - версия неизменяема после создания (в UI не показывать edit).

### 3. Модель PromptRating
- `app/models/prompt_rating.py`:
  - поля: `id`, `version_id` (FK, cascade), `user_id` (FK, cascade), `score` (Integer, 1–5), `comment` (Text, nullable), `created_at`;
  - `UniqueConstraint("version_id", "user_id")` — одна оценка на версию от пользователя;
  - `CheckConstraint("score BETWEEN 1 AND 5")`.

### 4. Миграция
- `flask db migrate -m "add prompt, version, rating"`.
- Проверить upgrade/downgrade.

### 5. Сервис версионирования
- `app/services/prompt_service.py`:
  - `create_prompt(user, data) -> Prompt`;
  - `create_version(prompt, data, change_note) -> PromptVersion` — вычисляет следующий `version_number` в транзакции;
  - обработка гонок: используй `SELECT ... FOR UPDATE` или повторную попытку при конфликте (задокументируй выбор).
- Проверка владения промптом до создания версии.

### 6. Маршруты промптов
- `app/prompts/routes.py` + `forms.py`:
  - `GET /prompts/` — список с фильтрами;
  - `GET/POST /prompts/new`;
  - `GET /prompts/<int:id>` — детали + список версий;
  - `POST /prompts/<int:id>/versions/new` — создание новой версии;
  - `GET /prompts/<int:id>/versions/<int:vid>` — просмотр версии;
  - `POST /prompts/<int:id>/versions/<int:vid>/rate` — оценка;
  - `POST /prompts/<int:id>/delete` — удаление промпта (каскадно версии и оценки).
- Проверка владения: чужие промпты/версии → 404.
- Шаблоны в `templates/prompts/`.

### 7. Оценки
- Форма оценки: score (1–5), comment.
- Серверная валидация диапазона.
- Повторная оценка той же версии — обновление существующей записи.
- Нельзя оценивать чужие версии.

### 8. Поиск и фильтрация
- `GET /prompts/?q=...&tag=...&ai_service=...`:
  - поиск по `title`, `purpose` (ILIKE);
  - фильтр по тегу;
  - фильтр по `ai_service`;
  - ограничение выборки текущим пользователем (на уровне SQL).
- Не загружать все записи в память.

### 9. UI
- Список промптов с формой фильтра.
- Страница промпта: список версий с номерами, датами, средним баллом.
- Форма создания версии.
- Блок оценок на странице версии.

### 10. Тесты
- `tests/test_prompts.py`:
  - создание промпта;
  - создание версии, номера последовательны;
  - старая версия остаётся после создания новой;
  - нельзя создать версию чужого промпта;
  - оценка вне 1–5 отклоняется;
  - повторная оценка обновляет существующую;
  - изоляция пользователей.
- `tests/test_search.py`:
  - поиск по title;
  - фильтр по тегу;
  - фильтр по сервису;
  - поиск не возвращает чужие промпты.
- Отсутствие оценок не ломает страницу (средний балл = None).

### 11. Документация
- README: раздел про промпты, версии, оценки, поиск.

## Проверки
```bash
pytest -q
ruff check .
ruff format --check .
flask db upgrade && flask db downgrade && flask db upgrade
