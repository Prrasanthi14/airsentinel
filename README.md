# 🌫️ AirSentinel

**An AI-powered, federated climate action platform that finds hyper-local pollution hotspots India's city monitors miss — and alerts the right authority before the smog hits.**

> Status: prototype in active development. Architecture, agents and data pipelines are scaffolded; see [Roadmap](#roadmap).

---

## The problem

Indian cities track air quality at a macro level through a limited number of monitoring stations. Hyper-local events — industrial emissions, stubble burning, garbage fires, seasonal smog — slip through the gaps. Without granular, real-time data, authorities can't coordinate a fast response, and people breathe the consequences.

## What AirSentinel does

| Capability | How |
|---|---|
| **Detect hidden hotspots** | Citizens upload a photo + location. Gemini's multimodal reasoning classifies the source (crop burning, industrial plume, garbage fire, dust) and severity. |
| **Verify from space** | Citizen reports are cross-checked against NASA FIRMS satellite fire detections and nearby ground AQI stations. Corroborated reports become confirmed hotspots. |
| **Forecast spikes** | AQI is forecast 24–72h ahead per city and economic corridor using historical AQI, wind, humidity and upwind fire counts. |
| **Alert the right authority** | An alert agent drafts an advisory (location, source, affected areas, recommended action) and routes it — pollution control board for industry, district administration for burning. |
| **Share models, not data** | Cities/states train forecasting models locally and share only model weights via federated learning — interoperable, privacy-preserving, and sovereign. |

## Architecture

```
 Citizen app (photo / sensor reading)      NASA FIRMS     OpenAQ / CPCB     Open-Meteo
            │                                   │               │               │
            ▼                                   ▼               ▼               ▼
   ┌─────────────────┐              ┌───────────────────────────────────────────────┐
   │ Evidence Agent  │              │            Ingestion → BigQuery               │
   │ (Gemini vision) │              └───────────────────────────────────────────────┘
   └────────┬────────┘                        │                         │
            ▼                                 ▼                         ▼
   ┌─────────────────┐              ┌──────────────────┐     ┌──────────────────────┐
   │ Satellite Agent │◄────────────►│  Forecast Agent  │◄───►│ Federated Layer      │
   │ (cross-verify)  │              │ (AQI 24–72h)     │     │ (Flower, per-city)   │
   └────────┬────────┘              └────────┬─────────┘     └──────────────────────┘
            └───────────────┬────────────────┘
                            ▼
                   ┌─────────────────┐        ┌──────────────────────────┐
                   │  Alert Agent    │───────►│ Authorities (SPCB/District)│
                   │ (advisory+route)│        └──────────────────────────┘
                   └────────┬────────┘
                            ▼
                  Dashboard (hotspot map, forecasts, alerts)
```

See [`docs/architecture.md`](docs/architecture.md) for details.

## Agents

- **`agents/evidence_agent.py`** — Gemini multimodal classifier for citizen photos; rejects irrelevant or fake submissions.
- **`agents/satellite_agent.py`** — Matches citizen reports to FIRMS fire points and AQI stations within a radius/time window; assigns a confidence score.
- **`agents/forecast_agent.py`** — AQI forecasting (BigQuery ML `ARIMA_PLUS` with weather features); wind-aware drift of pollution plumes.
- **`agents/alert_agent.py`** — Generates advisories with Gemini and routes them by source type and jurisdiction.
- **`agents/orchestrator.py`** — Runs the sense → verify → forecast → alert loop.

## Tech stack

- **AI:** Gemini (multimodal reasoning), Google Agent Development Kit (ADK)
- **Backend:** Python, FastAPI, hosted on Google Cloud Run
- **Data & ML:** Google BigQuery, BigQuery ML
- **Federated learning:** Flower (`flwr`)
- **Dashboard:** Streamlit + pydeck map
- **Data sources:** NASA FIRMS, OpenAQ, CPCB, Open-Meteo, citizen submissions

## Getting started

```bash
git clone https://github.com/<your-username>/airsentinel.git
cd airsentinel
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # add your API keys

uvicorn api.main:app --reload          # backend API
streamlit run dashboard/app.py         # dashboard
python -m federated.flower_sim         # federated learning simulation
```

## Demo scenario

1. NASA FIRMS shows fire clusters in Punjab; a citizen uploads a photo of crop burning near Sangrur.
2. The evidence agent classifies it as *crop burning, high severity*; the satellite agent confirms it against FIRMS.
3. Winds blow south-east; the forecast agent predicts Delhi NCR AQI spiking in ~36 hours.
4. The alert agent dispatches advisories to Punjab district administration and Delhi authorities.

## Roadmap

- [x] Problem framing, architecture and agent design
- [x] Repository scaffold and agent interfaces
- [ ] Live ingestion from FIRMS, OpenAQ and Open-Meteo into BigQuery
- [ ] Gemini evidence agent with a labelled demo image set
- [ ] Forecast model + wind-drift visualisation
- [ ] Federated simulation across 3 city clients
- [ ] Alert routing and dashboard polish
- [ ] Deploy to Cloud Run

## Designed as a Digital Public Good

Open source (MIT), open data sources, and a federated design so any Indian city or state can join without surrendering its data.

## License

MIT — see [LICENSE](LICENSE).
