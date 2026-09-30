"""Orchestrator: runs the sense -> verify -> forecast -> alert loop."""
from agents import alert_agent, evidence_agent, satellite_agent


def process_citizen_report(image_bytes: bytes, mime_type: str, lat: float, lon: float) -> dict:
    evidence = evidence_agent.classify_photo(image_bytes, mime_type, lat, lon)
    if not evidence.is_relevant:
        return {"status": "rejected", "reason": evidence.reasoning}

    fires = satellite_agent.fetch_fire_points()
    verification = satellite_agent.verify_report(lat, lon, fires)

    hotspot = {**evidence.__dict__, **verification}
    result = {"status": "recorded", "hotspot": hotspot}

    if verification["confirmed"] or evidence.severity >= 4:
        result["alert"] = alert_agent.draft_advisory(hotspot, forecast_summary="See city forecast")
    return result
