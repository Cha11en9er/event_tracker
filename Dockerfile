FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Копирование приложения
COPY . .

# Создание пользователя для безопасности
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Переменные окружения
ENV FLASK_APP=event_tracker.webui
ENV FLASK_ENV=production

# Порт для Gunicorn
EXPOSE 8082

# Запуск приложения через Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8082", "--workers", "3", "event_tracker.webui:app"] 