# ──────────────────────────────────────────────────────────────────────────────
# AirSentinel — Streamlit dashboard
# Deployable to Google Cloud Run
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Dashboard + shared data
COPY dashboard/ ./dashboard/
COPY data/      ./data/
COPY agents/    ./agents/
COPY federated/ ./federated/

# Streamlit config: disable CORS restriction and browser auto-open
RUN mkdir -p /app/.streamlit && printf \
    "[server]\nheadless = true\nenableCORS = false\nenableXsrfProtection = false\nport = $PORT\n\n[browser]\ngatherUsageStats = false\n" \
    > /app/.streamlit/config.toml

CMD ["sh", "-c", "streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0"]
