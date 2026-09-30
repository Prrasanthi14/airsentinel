"""Evidence Agent: classifies citizen-submitted photos using Gemini multimodal reasoning."""
import json
import os
from dataclasses import dataclass

from google import genai
from google.genai import types

SOURCE_TYPES = ["crop_burning", "industrial_plume", "garbage_fire", "dust", "vehicular_smog", "none"]

PROMPT = f"""You are an air-pollution evidence analyst for Indian authorities.
Look at the photo and return ONLY JSON with keys:
  source_type: one of {SOURCE_TYPES}
  severity: integer 1-5 (5 = dense, widespread smoke)
  confidence: float 0-1
  is_relevant: boolean (false if the photo does not show outdoor air pollution)
  reasoning: one short sentence
"""


@dataclass
class Evidence:
    source_type: str
    severity: int
    confidence: float
    is_relevant: bool
    reasoning: str
    lat: float
    lon: float


def classify_photo(image_bytes: bytes, mime_type: str, lat: float, lon: float) -> Evidence:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime_type), PROMPT],
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    result = json.loads(response.text)
    return Evidence(lat=lat, lon=lon, **result)
