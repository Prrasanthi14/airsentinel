"""Satellite Agent: cross-verifies citizen reports against NASA FIRMS fire detections and AQI stations."""
import io
import math
import os

import pandas as pd
import requests

FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/VIIRS_SNPP_NRT/{bbox}/{days}"
OPENAQ_URL = "https://api.openaq.org/v3/locations"

# Default bounding box: Punjab – Haryana – Delhi NCR corridor (west, south, east, north)
NORTH_INDIA_BBOX = "73.8,27.5,78.0,32.5"


def fetch_fire_points(bbox: str = NORTH_INDIA_BBOX, days: int = 1) -> pd.DataFrame:
    url = FIRMS_URL.format(key=os.environ["FIRMS_MAP_KEY"], bbox=bbox, days=days)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return pd.read_csv(io.StringIO(resp.text))


def fetch_aqi_stations(lat: float, lon: float, radius_m: int = 25000) -> list[dict]:
    resp = requests.get(
        OPENAQ_URL,
        params={"coordinates": f"{lat},{lon}", "radius": radius_m, "limit": 20},
        headers={"X-API-Key": os.environ["OPENAQ_API_KEY"]},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def verify_report(lat: float, lon: float, fires: pd.DataFrame, radius_km: float = 5.0) -> dict:
    """Return how many satellite fire detections corroborate a citizen report."""
    if fires.empty:
        return {"corroborating_fires": 0, "confirmed": False}
    dists = fires.apply(lambda r: haversine_km(lat, lon, r["latitude"], r["longitude"]), axis=1)
    nearby = int((dists <= radius_km).sum())
    return {"corroborating_fires": nearby, "confirmed": nearby > 0}
