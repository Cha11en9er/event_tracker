FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including locale support
RUN apt-get update && apt-get install -y \
    locales \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen

# Set environment variables for locale
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY event_tracker_webui/src /app

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/app

# Expose the port Gunicorn will run on
EXPOSE 8000

# Run with Gunicorn using gevent worker
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--worker-class", "gevent", "website.app:app"] 