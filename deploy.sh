#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# deploy.sh — Build & deploy AirSentinel to Google Cloud Run
#
# Usage:
#   chmod +x deploy.sh
#   ./deploy.sh
#
# Prerequisites:
#   - gcloud CLI installed and authenticated   (gcloud auth login)
#   - Docker running locally
#   - APIs enabled:  Cloud Run, Cloud Build, Container Registry or Artifact Registry
#
# Environment variables are set AFTER deployment via:
#   gcloud run services update <service> --set-env-vars KEY=VALUE --region REGION
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
PROJECT_ID="gen-lang-client-0469618448"
REGION="us-central1"
API_SERVICE="airsentinel-api"
DASH_SERVICE="airsentinel-dashboard"
API_IMAGE="gcr.io/${PROJECT_ID}/${API_SERVICE}"
DASH_IMAGE="gcr.io/${PROJECT_ID}/${DASH_SERVICE}"

# ── Colours ───────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()  { echo -e "${BLUE}[deploy]${NC} $*"; }
ok()   { echo -e "${GREEN}[done]${NC}  $*"; }
warn() { echo -e "${YELLOW}[warn]${NC}  $*"; }

# ── 0. Validate prerequisites ─────────────────────────────────────────────────
log "Using GCP project: ${PROJECT_ID} | region: ${REGION}"
gcloud config set project "${PROJECT_ID}"

log "Enabling required GCP APIs (safe to run repeatedly)..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  --project="${PROJECT_ID}"

# ── 1. Configure Docker for GCR ──────────────────────────────────────────────
log "Configuring Docker auth for GCR..."
gcloud auth configure-docker --quiet

# ── 2. Build & push FastAPI image ─────────────────────────────────────────────
log "Building FastAPI backend image..."
docker build -t "${API_IMAGE}:latest" -f Dockerfile .
log "Pushing FastAPI image to GCR..."
docker push "${API_IMAGE}:latest"

# ── 3. Build & push Streamlit image ───────────────────────────────────────────
log "Building Streamlit dashboard image..."
docker build -t "${DASH_IMAGE}:latest" -f dashboard/Dockerfile .
log "Pushing Streamlit image to GCR..."
docker push "${DASH_IMAGE}:latest"

# ── 4. Deploy FastAPI service ─────────────────────────────────────────────────
log "Deploying ${API_SERVICE} to Cloud Run..."
gcloud run deploy "${API_SERVICE}" \
  --image="${API_IMAGE}:latest" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=5 \
  --project="${PROJECT_ID}"

API_URL=$(gcloud run services describe "${API_SERVICE}" \
  --region="${REGION}" --project="${PROJECT_ID}" \
  --format="value(status.url)")
ok "FastAPI backend live → ${API_URL}"

# ── 5. Deploy Streamlit service ───────────────────────────────────────────────
log "Deploying ${DASH_SERVICE} to Cloud Run..."
gcloud run deploy "${DASH_SERVICE}" \
  --image="${DASH_IMAGE}:latest" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=3 \
  --project="${PROJECT_ID}"

DASH_URL=$(gcloud run services describe "${DASH_SERVICE}" \
  --region="${REGION}" --project="${PROJECT_ID}" \
  --format="value(status.url)")
ok "Streamlit dashboard live → ${DASH_URL}"

# ── 6. Remind user to set env vars ────────────────────────────────────────────
warn "⚠️  Don't forget to set your secret environment variables!"
echo ""
echo "Run the following, replacing placeholder values with your real keys:"
echo ""
echo "  gcloud run services update ${API_SERVICE} \\"
echo "    --region=${REGION} \\"
echo "    --set-env-vars \\"
echo "    GEMINI_API_KEY=<your-key>,\\"
echo "    GEMINI_MODEL=gemini-2.5-flash,\\"
echo "    FIRMS_MAP_KEY=<your-key>,\\"
echo "    OPENAQ_API_KEY=<your-key>,\\"
echo "    GCP_PROJECT=${PROJECT_ID},\\"
echo "    BQ_DATASET=airsentinel"
echo ""
echo "  gcloud run services update ${DASH_SERVICE} \\"
echo "    --region=${REGION} \\"
echo "    --set-env-vars GCP_PROJECT=${PROJECT_ID},BQ_DATASET=airsentinel"
echo ""
echo "──────────────────────────────────────────"
echo " FastAPI  → ${API_URL}"
echo " Dashboard → ${DASH_URL}"
echo "──────────────────────────────────────────"
