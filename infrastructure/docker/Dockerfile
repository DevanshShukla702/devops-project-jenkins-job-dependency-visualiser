# ═══════════════════════════════════════════════
# FlowTrace — Production Dockerfile
# ═══════════════════════════════════════════════
FROM python:3.12-slim

# Security: don't run as root
RUN groupadd -r flowtrace && useradd -r -g flowtrace flowtrace

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker cache optimization
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create directories for logs and database
RUN mkdir -p /app/src/main/python/logs \
    && chown -R flowtrace:flowtrace /app

# Switch to non-root user
USER flowtrace

# Environment defaults
ENV FLASK_ENV=production \
    PORT=5000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Production WSGI server
CMD ["gunicorn", \
    "--bind", "0.0.0.0:5000", \
    "--workers", "4", \
    "--threads", "2", \
    "--timeout", "120", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "src.main.python.api.app:app"]
