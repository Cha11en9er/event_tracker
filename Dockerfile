FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including locale support
RUN apt-get update && apt-get install -y \
    locales \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i ru_RU -c -f CP1251 -A /usr/share/locale/locale.alias ru_RU.CP1251

# Set environment variables for locale
ENV LANG ru_RU.CP1251
ENV LANGUAGE ru_RU.CP1251
ENV LC_ALL ru_RU.CP1251

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