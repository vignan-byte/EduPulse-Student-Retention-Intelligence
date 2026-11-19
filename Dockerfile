FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    FLASK_ENV=production

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and artifacts
COPY . .

# Ensure unprivileged app user with proper write permissions for SQLite DB
RUN useradd --create-home --uid 10001 appuser && \
    mkdir -p /app/local_demo /tmp/edupulse && \
    chown -R appuser:appuser /app /tmp/edupulse

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD curl -f http://127.0.0.1:${PORT:-5000}/api/health/live || exit 1

CMD ["sh", "-c", "exec gunicorn --config gunicorn.conf.py wsgi:application"]
