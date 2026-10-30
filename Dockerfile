# Dockerfile для PromptFlow (Flask-приложение)
FROM python:3.11-slim

WORKDIR /app

# Системные зависимости для psycopg2 и сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код приложения
COPY . .

# Переменные окружения по умолчанию (переопределяются через .env / compose)
ENV FLASK_ENV=production
ENV FLASK_APP=app:create_app
ENV SECRET_KEY=""
ENV DATABASE_URL=""

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
