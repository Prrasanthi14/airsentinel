# ──────────────────────────────────────────────────────────────────────────────
# AirSentinel — FastAPI backend
# Deployable to Google Cloud Run
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Keeps Python from generating .pyc files and enables stdout/stderr logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install dependencies first (layer-cached when only code changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY agents/ ./agents/
COPY api/    ./api/
COPY data/   ./data/
COPY federated/ ./federated/

# Cloud Run injects $PORT; Uvicorn binds to it at runtime
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port $PORT"]
