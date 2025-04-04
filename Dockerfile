FROM python:3.10-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 8000

# Run with Gunicorn using gevent worker
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--worker-class", "gevent", "website.app:app"] 