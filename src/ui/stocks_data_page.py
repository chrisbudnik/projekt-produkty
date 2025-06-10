import streamlit as st
import pandas as pd
import plotly.graph_objects as go




# --- Load Data ---
def load_data(path):
    return pd.read_csv(path, parse_dates=["Date"])


def stocks_data_page():
    """
    Main function to render the stocks data page.
    This function sets up the Streamlit page with controls and displays
    a candlestick chart and a data table for stock prices.
    """
    data = load_data("src/example_wig20_data.csv")

    st.title("📈 Notowania spółek indeksu WIG20")

    # --- Top Controls ---
    col1, col2, col3 = st.columns(3)

    with col1:
        ticker = st.selectbox("Wybierz symbol:", data["Ticker"].unique())

    with col2:
        min_date = data["Date"].min()
        max_date = data["Date"].max()
        start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)

    with col3:
        end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

    # --- Validation ---
    if start_date > end_date:
        st.error("🚫 Data początkowa zakresu musi być mniejsza od końcowej.")

    # --- Filter Data ---
    df = data[
        (data["Ticker"] == ticker) &
        (data["Date"] >= pd.to_datetime(start_date)) &
        (data["Date"] <= pd.to_datetime(end_date))
    ].sort_values("Date")


    # --- Two Columns: Chart & Table ---
    left, right = st.columns([3, 2])

    with left:
        st.subheader("🕯️ Wykres Świecowy")

        if df.empty:
            st.warning("Brak danych dla wskazanego zakresu / symbolu.")
        else:
            fig = go.Figure(data=[
                go.Candlestick(
                    x=df["Date"],
                    open=df["Open"],
                    high=df["High"],
                    low=df["Low"],
                    close=df["Close"],
                    name="Candlestick"
                )
            ])
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price",
                xaxis_rangeslider_visible=False,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("📋 Dane tabelaryczne")
        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)