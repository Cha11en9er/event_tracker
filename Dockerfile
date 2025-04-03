FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn gevent

# Копирование приложения
COPY . .

# Создание пользователя для безопасности
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Переменные окружения
ENV FLASK_APP=event_tracker.webui
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Порт для Gunicorn
EXPOSE 8082

# Создание файла конфигурации Gunicorn
RUN echo 'import multiprocessing\n\
bind = "0.0.0.0:8082"\n\
workers = multiprocessing.cpu_count() * 2 + 1\n\
worker_class = "gevent"\n\
keepalive = 60\n\
timeout = 60\n\
threads = 2\n\
max_requests = 1000\n\
max_requests_jitter = 50\n\
graceful_timeout = 30\n\
errorlog = "-"\n\
loglevel = "info"\n\
accesslog = "-"\n\
access_log_format = "%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\" %(T)s"' > gunicorn.conf.py

# Запуск приложения через Gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "event_tracker.webui:app"] 