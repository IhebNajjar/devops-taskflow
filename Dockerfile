# ==============================================================================
# TaskFlow Production Dockerfile
# Conforms to DevOps Module Standards:
#  - Tag explicite: python:3.11-slim (never latest)
#  - Utilisateur non-root: appuser (UID 10001)
#  - HEALTHCHECK instruction sur /health
# ==============================================================================

# 1. Base image with explicit tag
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set working directory
WORKDIR /app

# 2. Create non-root system user and group (Point 3)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# 3. Install Python dependencies with layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. Copy application source code and set ownership to non-root user
COPY --chown=appuser:appgroup . .

# 5. Switch to non-root user (Point 3)
USER appuser

# Expose HTTP port
EXPOSE 8000

# 6. Container HEALTHCHECK (Point 3)
# Uses Python's standard urllib to check /health endpoint without requiring curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

# 7. Start production server
CMD ["python", "main.py"]
