import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from openai import OpenAI

from llm.responses import get_llm_response
from llm.prompts import STOCK_EXPERT_ANALYST



# --- Load Data ---
def load_data(path):
    return pd.read_csv(path, parse_dates=["Date"])


def filter_data(df, ticker, start_date, end_date):
    """
    Filter the DataFrame based on the selected ticker and date range.
    """
    return df[
        (df["Ticker"] == ticker) &
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ].sort_values("Date")


def expert_chat_component(company: str, date_from: str, date_to: str, data: str):
    """
    A simple chat input component for user interaction.
    This function allows users to input text and displays the input back to them.
    """
    st.subheader("💬 Chat with Expert")
    
    prompt = st.chat_input("Say something")
    if prompt:
        st.write(f"Pytanie do eksperta: {prompt}")
        
        full_prompt = STOCK_EXPERT_ANALYST.format(
            company=company, 
            prompt=prompt, 
            date_from=date_from, 
            date_to=date_to, 
            data=data
        )

        with st.spinner("Ekspert analizuje dane..."):
            client = OpenAI()
            response = get_llm_response(client, full_prompt)

        st.success("Odpowiedź eksperta:")
        st.write(response)


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
        min_date = data["Date"].min().date()
        max_date = data["Date"].max().date()
        start_date = st.date_input("Start Date", value=min_date, )

    with col3:
        end_date = st.date_input("End Date", value=max_date, )


    # --- Validation ---
    if start_date > end_date:
        st.error(
            "🚫 Data początkowa zakresu musi być mniejsza od końcowej."
        )

    if start_date < min_date or end_date > max_date:
        st.error(
            f"🚫 Zakres dat musi być pomiędzy {min_date.strftime('%Y-%m-%d')}"
            f" a {max_date.strftime('%Y-%m-%d')}."
        )

    # --- Filter Data ---
    df = filter_data(data, ticker, start_date, end_date)

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

    expert_chat_component(
        company=ticker,
        date_from=start_date.strftime("%Y-%m-%d"),
        date_to=end_date.strftime("%Y-%m-%d"),
        data=df.to_json(orient="records")
    )


