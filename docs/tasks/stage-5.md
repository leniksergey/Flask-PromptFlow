# Этап 5 — Интерфейс и завершение MVP

> Прочитай `AGENTS.md` полностью и предыдущие `stage-*.md`. Проверь, что этапы 1–4 завершены. Этап 5 — финальная полировка и подготовка репозитория к публикации.

## Цель этапа
Привести UI к единому Bootstrap-дизайну, обеспечить адаптивность, настроить CI, обновить README, проверить полный сценарий MVP.

## Задачи

### 1. Базовый шаблон и навигация
- `templates/base.html`:
  - Bootstrap 5 через CDN или локальный static;
  - навбар: логотип, ссылки на dashboard, projects, prompts, login/logout;
  - flash-сообщения (success, danger, info);
  - блок `{% block content %}`;
  - footer с версией и ссылкой на репозиторий (без секретов).
- Адаптивность: навбар сворачивается на мобильных (`navbar-toggler`).

### 2. Единый стиль страниц
- Все формы — через Bootstrap (`form-control`, `form-select`, `is-invalid` + `invalid-feedback` для ошибок WTForms).
- Кнопки действий: primary / secondary / danger.
- Таблицы: `table table-hover`, адаптивная обёртка `table-responsive`.
- Карточки для dashboard.
- Единый шаблон подтверждения удаления (`confirm.html` или модальное окно Bootstrap).

### 3. Сообщения и ошибки
- Flash-сообщения на всех действиях (создание, изменение, удаление, ошибки валидации).
- Страницы 403/404/500 оформлены в общем стиле.
- Не показывать traceback в production.

### 4. Статические ресурсы
- `app/static/css/style.css` — минимальные кастомные стили поверх Bootstrap.
- `app/static/js/app.js` — только необходимое (подтверждение удаления, авто-скрытие flash).

### 5. Ruff и CI
- Проверить `pyproject.toml`: `line-length`, `target-version`, правила Ruff.
- `.github/workflows/ci.yml`:
  - матрица Python 3.11 и 3.12;
  - шаги: checkout, setup-python, install deps, `ruff check`, `ruff format --check`, `pytest -q`.

### 6. README — финальная версия
Разделы:
- описание проблемы и аудитории;
- основные функции;
- стек;
- архитектура и модели;
- требования к окружению;
- установка и запуск через Docker Compose;
- миграции (`flask db upgrade`) и запуск тестов (`pytest -q`);
- примеры экспорта;
- известные ограничения.

### 7. Проверка полного сценария MVP
Пройти вручную по критериям раздела 14 `AGENTS.md`:
1. клонировать репозиторий, настроить `.env`, `docker compose up`;
2. `flask db upgrade`;
3. зарегистрировать пользователя;
4. создать проект и 2–3 сцены;
5. создать промпт и 2 версии;
6. оценить версии, увидеть средний балл;
7. экспортировать проект в Markdown и JSON;
8. проверить изоляцию прав между пользователями;
9. запустить `pytest -q` — все тесты зелёные.

### 8. Финальная проверка репозитория
- `git status` — нет лишних файлов (`.env`, `*.pyc`, `.venv`).
- `grep -r "password\|secret\|token"` по коду — нет захардкоженных секретов.
- `.gitignore` покрывает все служебные файлы.
- `.env.example` содержит только безопасные примеры.

## Проверки
```bash
pytest -q
ruff check .
ruff format --check .
docker compose up --build -d
curl -fsS http://localhost:5000/health
git status
