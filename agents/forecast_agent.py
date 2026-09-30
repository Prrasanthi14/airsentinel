"""Forecast Agent: predicts AQI 24-72h ahead per city using BigQuery ML ARIMA_PLUS with weather features."""
import os

import requests
from google.cloud import bigquery

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

TRAIN_SQL = """
CREATE OR REPLACE MODEL `{project}.{dataset}.aqi_forecast`
OPTIONS(
  model_type = 'ARIMA_PLUS_XREG',
  time_series_timestamp_col = 'ts',
  time_series_data_col = 'pm25',
  time_series_id_col = 'city'
) AS
SELECT ts, city, pm25, wind_speed, wind_dir, humidity, upwind_fire_count
FROM `{project}.{dataset}.aqi_hourly`
"""


def fetch_weather(lat: float, lon: float) -> dict:
    resp = requests.get(
        OPEN_METEO_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "hourly": "wind_speed_10m,wind_direction_10m,relative_humidity_2m",
            "forecast_days": 3,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["hourly"]


def train_model() -> None:
    client = bigquery.Client(project=os.environ["GCP_PROJECT"])
    client.query(TRAIN_SQL.format(project=os.environ["GCP_PROJECT"], dataset=os.environ["BQ_DATASET"])).result()


def forecast(city: str, horizon_hours: int = 72):
    client = bigquery.Client(project=os.environ["GCP_PROJECT"])
    sql = f"""
    SELECT * FROM ML.FORECAST(
      MODEL `{os.environ['GCP_PROJECT']}.{os.environ['BQ_DATASET']}.aqi_forecast`,
      STRUCT({horizon_hours} AS horizon, 0.9 AS confidence_level),
      (SELECT * FROM `{os.environ['GCP_PROJECT']}.{os.environ['BQ_DATASET']}.weather_future`))
    WHERE city = @city
    """
    job = client.query(sql, job_config=bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("city", "STRING", city)]))
    return job.to_dataframe()


def spike_expected(forecast_df, threshold_pm25: float = 250.0) -> bool:
    """PM2.5 above 250 µg/m³ corresponds to the 'Severe' band of India's AQI."""
    return bool((forecast_df["forecast_value"] > threshold_pm25).any())
