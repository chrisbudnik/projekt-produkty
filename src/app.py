from enum import Enum
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

from ui.stocks_data_page import stocks_data_page
from ui.weather_data_page import weather_forecast_page, zmień_miasto
from ui.settings_page import settings_page

# --- Config file ---
config_path = 'config/config.json'

# Jeśli nie istnieje plik konfiguracyjny, utwórz domyślne dane
if not os.path.exists(config_path):
    config_data = pd.DataFrame([{
        "city_name": "Warszawa",
        "latitude": 52.2297,
        "longitude": 21.0122,
        "last_weather_request": pd.NA
    }])
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    config_data.to_json(config_path, orient='records', indent=4)

# --- Page config ---
st.set_page_config(page_title="Weather + Stock AI APP", layout="wide")

# --- Sidebar ---
st.sidebar.title("📚 Menu")

page = st.sidebar.selectbox(
    "Wybierz stronę:",
    ("📈 Notowania Spółek", "🌦️ Pogoda", "⚙️ Ustawienia")
)

# --- Page Routing ---
if page == "📈 Notowania Spółek":
    stocks_data_page()
elif page == "🌦️ Pogoda":
    weather_forecast_page()
elif page == "⚙️ Ustawienia":
    settings_page()
