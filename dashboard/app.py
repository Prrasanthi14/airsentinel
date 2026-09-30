"""AirSentinel dashboard: hotspot map, forecasts and alerts."""
import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="AirSentinel", page_icon="🌫️", layout="wide")
st.title("🌫️ AirSentinel — Pollution Hotspot Command Centre")

hotspots = pd.read_csv("data/sample_hotspots.csv")

col1, col2, col3 = st.columns(3)
col1.metric("Active hotspots", len(hotspots))
col2.metric("Satellite-confirmed", int(hotspots["confirmed"].sum()))
col3.metric("Alerts dispatched", int((hotspots["severity"] >= 4).sum()))

st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(latitude=29.5, longitude=76.0, zoom=6),
    layers=[pdk.Layer(
        "ScatterplotLayer", hotspots,
        get_position="[lon, lat]", get_radius="severity * 4000",
        get_fill_color="[220, 60, 40, 160]", pickable=True,
    )],
    tooltip={"text": "{source_type}\nSeverity {severity}\n{place}"},
))

st.subheader("Hotspot log")
st.dataframe(hotspots, use_container_width=True)
