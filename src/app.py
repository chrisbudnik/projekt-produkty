from enum import Enum
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ui.stocks_data_page import stocks_data_page
from ui.weather_data_page import weather_forecast_page, zmień_miasto
from ui.settings import settings_page




# --- Page config ---
st.set_page_config(page_title="Weather + Stock AI APP", layout="wide")


st.sidebar.title("📚 Menu")

page = st.sidebar.selectbox(
    "Wybierz stronę:", ("📈 Notowania Spółek", 
                        "🌦️ Pogoda")
    )

# --- Page Routing ---
if page == "📈 Notowania Spółek":
    stocks_data_page()

elif page == "🌦️ Pogoda":
    weather_forecast_page()

