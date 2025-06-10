from enum import Enum
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ui.stocks_data_page import stocks_data_page

# --- Page config ---
st.set_page_config(page_title="Weather + Stock AI APP", layout="wide")


st.sidebar.title("📚 Menu")

page = st.sidebar.selectbox(
    "Wybierz stronę:", ("📈 Notowania Spółek", "🌦️ Pogoda")
    )

# --- Page Routing ---
if page == "📈 Notowania Spółek":
    stocks_data_page()

elif page == "🌦️ Pogoda":
    st.title("🌦️ Pogoda")
    st.info("in progress...")