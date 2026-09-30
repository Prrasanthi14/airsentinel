# AirSentinel Architecture

## Agent loop
1. **Sense** — citizen photos/sensor readings arrive via the API; FIRMS, OpenAQ and Open-Meteo are ingested into BigQuery on a schedule.
2. **Verify** — the Evidence Agent (Gemini multimodal) classifies source and severity; the Satellite Agent corroborates with FIRMS fire points within 5 km and nearby AQI stations.
3. **Forecast** — the Forecast Agent runs BigQuery ML `ARIMA_PLUS_XREG` per city with wind, humidity and upwind fire counts as regressors to predict 24–72h AQI.
4. **Act** — the Alert Agent drafts an advisory with Gemini and routes it by source type and jurisdiction.

## Federated model sharing
Each city/state runs a Flower client that trains on local data. Only model weights are sent to the aggregator (FedAvg); the shared national model is sent back. Raw citizen and sensor data never leaves the jurisdiction.

## Deployment
- FastAPI backend and Streamlit dashboard on Google Cloud Run
- BigQuery for storage, analytics and forecasting
- Cloud Scheduler for periodic ingestion

## Interoperability
Open REST APIs, open data sources and an open-source licence so any city or state can plug in as a new federated client.
