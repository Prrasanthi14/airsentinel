"""AirSentinel API (FastAPI) — deployable to Google Cloud Run."""
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile

from agents import orchestrator, satellite_agent

load_dotenv()
app = FastAPI(title="AirSentinel", description="Hyper-local pollution hotspot detection and alerts")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reports")
async def submit_report(photo: UploadFile = File(...), lat: float = Form(...), lon: float = Form(...)):
    """Citizen submits a photo + location; runs the full agent loop."""
    image = await photo.read()
    return orchestrator.process_citizen_report(image, photo.content_type or "image/jpeg", lat, lon)


@app.get("/fires")
def fires(days: int = 1):
    """Latest NASA FIRMS fire detections for the North India corridor."""
    return satellite_agent.fetch_fire_points(days=days).to_dict(orient="records")
