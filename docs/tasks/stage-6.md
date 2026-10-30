# Stage 6: Аудит и исправление верстки интерфейса (UI/UX Audit)

## 1. Проблема и цели
В ходе локального тестирования MVP-версии **PromptFlow** выявлены значительные сбои в отображении HTML-шаблонов:
1. **Шапка сайта (`base.html`):** Элементы навигации (`email`, кнопка `Выйти` / ссылки `Вход` и `Регистрация`) съезжают за пределы навбара, выравнивание по флексбоксам сломано.
2. **Отображение CSRF-токенов:** Вызов `{{ csrf_token() }}` в виде отдельной строки выводит сырой токен `IjIzMmYw...` прямо на экран вместо скрытого инпута (`<input type="hidden">`).
3. **Карточки проектов и списки:** Заголовки, кнопки действий и бэджи с тегами расползаются при изменении ширины экрана.
4. **Отсутствие единого стиля:** Отступы (`padding`, `margin`) и выравнивание элементов различаются от страницы к странице.

---

## 2. Чек-лист проверки шаблонов (Audit Checklist)

### A. Шапка и навигация (`app/templates/base.html`)
- [ ] Обернуть все элементы навигационной панели в правильные Flex-контейнеры Bootstrap 5 (`d-flex`, `align-items-center`).
- [ ] Разделить навигацию на две части: левая (`me-auto`) для ссылок "Дашборд", "Проекты", "Промпты" и правая (`ms-auto`) для профиля пользователя и кнопки "Выйти".
- [ ] Заменить форму с голой кнопкой выключения на корректно стилизованную ссылку/кнопку внутри `nav-item`.
- [ ] Проверить корректность закрывающих тегов `</div>` и `</ul>`.

### B. Главная страница / Дашборд (`app/templates/main/dashboard.html`)
- [ ] Проверить выравнивание статистических карточек (Проекты, Сцены, Промпты, Версии).
- [ ] Убедиться, что приветствие и текущий email не разрывают шапку.

### C. Список проектов (`app/templates/projects/list.html`)
- [ ] Заменить вызов `{{ csrf_token() }}` во всех `POST`-формах на `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`.
- [ ] Перевести кнопку "Редактировать" с `POST`-формы на прямую `GET`-ссылку (`<a>`).
- [ ] Настроить заголовок и кнопку "+ Новый проект" в единую флекс-строку (`d-flex justify-content-between align-items-center`).

### D. Детали проекта и сцены (`app/templates/projects/detail.html`)
- [ ] Проверить адаптивность таблицы или карточек сцен.
- [ ] Выровнять кнопки экспорта (JSON / Markdown) и добавления сцен.

---

## 3. Эталонный код исправленных шаблонов

### 3.1. Исправленный `app/templates/base.html`
```html
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}PromptFlow{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
</head>
<body class="d-flex flex-column min-vh-100 bg-light">

<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4 shadow-sm">
    <div class="container">
        <a class="navbar-brand fw-bold" href="{{ url_for('main.index') }}">PromptFlow</a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                {% if current_user.is_authenticated %}
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint == 'main.dashboard' %}active{% endif %}" href="{{ url_for('main.dashboard') }}">Дашборд</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint == 'projects.list' %}active{% endif %}" href="{{ url_for('projects.list') }}">Проекты</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint == 'prompts.list' %}active{% endif %}" href="{{ url_for('prompts.list') }}">Промпты</a>
                    </li>
                {% endif %}
            </ul>
            
            <ul class="navbar-nav ms-auto align-items-center gap-2">
                {% if current_user.is_authenticated %}
                    <li class="nav-item">
                        <span class="navbar-text text-light me-2">{{ current_user.email }}</span>
                    </li>
                    <li class="nav-item">
                        <form method="POST" action="{{ url_for('auth.logout') }}" class="m-0">
                            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                            <button type="submit" class="btn btn-outline-light btn-sm">Выйти</button>
                        </form>
                    </li>
                {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.login') }}">Вход</a>
                    </li>
                    <li class="nav-item">
                        <a class="btn btn-primary btn-sm ms-2" href="{{ url_for('auth.register') }}">Регистрация</a>
                    </li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>

<main class="container flex-grow-1">
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show mb-4" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    {% block content %}{% endblock %}
</main>

<footer class="border-top mt-auto py-3 bg-white text-center text-muted small">
    <div class="container">
        PromptFlow v0.1.0 &mdash; MVP. 
        <a href="https://github.com" class="text-muted text-decoration-underline" target="_blank">Исходный код на GitHub</a> 
        &mdash; в репозитории нет секретов.
    </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
```

### 3.2. Исправленный `app/templates/projects/list.html`
```html
{% extends "base.html" %}

{% block title %}Проекты — PromptFlow{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h2 class="h3 mb-0">Мои проекты</h2>
    <a href="{{ url_for('projects.new') }}" class="btn btn-primary">+ Новый проект</a>
</div>

{% if projects %}
    <div class="row g-4">
        {% for project in projects %}
            <div class="col-md-6 col-lg-4">
                <div class="card h-100 shadow-sm border-0">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title fw-bold text-dark">{{ project.title }}</h5>
                        {% if project.description %}
                            <p class="card-text text-muted small flex-grow-1">
                                {{ project.description[:120] }}{% if project.description|length > 120 %}...{% endif %}
                            </p>
                        {% endif %}
                        <div class="mb-3 mt-2">
                            <span class="badge bg-secondary me-1">{{ project.content_format or '—' }}</span>
                            <span class="badge bg-info text-dark">{{ project.visual_style or '—' }}</span>
                        </div>
                        <a href="{{ url_for('projects.detail', id=project.id) }}" class="btn btn-outline-primary btn-sm w-100 mt-auto">Открыть</a>
                    </div>
                    <div class="card-footer bg-light border-0 d-flex justify-content-between align-items-center py-2">
                        <a href="{{ url_for('projects.edit', id=project.id) }}" class="btn btn-sm btn-link text-decoration-none text-secondary p-0">Редактировать</a>
                        
                        <form method="POST" action="{{ url_for('projects.delete', id=project.id) }}" class="d-inline" data-confirm="Удалить проект и все его сцены?">
                            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                            <button type="submit" class="btn btn-sm btn-link text-decoration-none text-danger p-0">Удалить</button>
                        </form>
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>
{% else %}
    <div class="card text-center py-5 border-0 shadow-sm">
        <div class="card-body">
            <p class="text-muted mb-3">У вас пока нет проектов. Создайте первый проект!</p>
            <a href="{{ url_for('projects.new') }}" class="btn btn-primary btn-sm">+ Новый проект</a>
        </div>
    </div>
{% endif %}
{% endblock %}
```

---

## 4. План выполнения правок
1. Обновить `app/templates/base.html` предложенным кодом.
2. Обновить `app/templates/projects/list.html`.
3. Обновить страницу дешборда (`app/templates/main/dashboard.html`) при необходимости.
4. Выполнить перезагрузку страницы в браузере с очисткой кэша (`Ctrl + F5` или `Cmd + Shift + R`).
5. Проверить адаптивность в мобильном режиме (`Responsive Mode` в DevTools).