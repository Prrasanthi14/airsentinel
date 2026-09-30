"""Alert Agent: drafts advisories with Gemini and routes them to the right authority."""
import os

from google import genai

ROUTING = {
    "crop_burning": "District Administration & State Agriculture Department",
    "industrial_plume": "State Pollution Control Board",
    "garbage_fire": "Municipal Corporation",
    "dust": "Municipal Corporation & PWD",
    "vehicular_smog": "Traffic Police & Transport Department",
}


def route(source_type: str) -> str:
    return ROUTING.get(source_type, "State Pollution Control Board")


def draft_advisory(hotspot: dict, forecast_summary: str) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = f"""Draft a concise early-warning advisory (max 120 words) for Indian authorities.
Hotspot: {hotspot}
Forecast: {forecast_summary}
Include: location, likely source, affected areas downwind, recommended immediate action."""
    response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt)
    return {"recipient": route(hotspot.get("source_type", "")), "advisory": response.text}
