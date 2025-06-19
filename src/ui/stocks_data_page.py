import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.graph_objects as go
from openai import OpenAI

from llm.responses import get_llm_response
from llm.prompts import STOCK_EXPERT_ANALYST
from stock_exchange_data import WIG20_TICKERS



# --- Load Data ---
def load_data(path: str) -> pd.DataFrame:
    """
    Load stock data from a CSV file and parse the 'Date' column as datetime."""
    return pd.read_csv(path, parse_dates=["Date"])


def select_dataset(
        timeframe: str = "Daily"
    ) -> pd.DataFrame:
    """
    Select the dataset based on the specified timeframe.
    Available options are 'Daily' and 'Hourly'.
    """
    if timeframe not in ["Daily", "Hourly"]:
        raise st.error("Błędny zakres czasowy. Wybierz 'Daily' lub 'Hourly'."
)
    dataset_paths = {
        "Daily": "src/datasets/example_wig20_data_daily.csv",
        "Hourly": "src/datasets/example_wig20_data_hourly.csv",
    }
    dataset_path = dataset_paths[timeframe]
    return load_data(dataset_path)


def filter_data(
        df: pd.DataFrame, 
        ticker: str, 
        start_date: datetime,
        end_date: datetime, 
    ) -> pd.DataFrame:
    """
    Filter the DataFrame based on the selected ticker and date range.
    """
    return df[
        (df["Ticker"] == ticker) &
        (df["Date"] >= start_date.strftime("%Y%m%d 00:00:00")) &
        (df["Date"] <= end_date.strftime("%Y%m%d 23:59:59"))
    ].sort_values("Date")


def expert_chat_component(
        company: str, 
        date_from: str, 
        date_to: str, 
        data: str
    ) -> None:
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


def select_chart_type(
        df: pd.DataFrame, 
        chart_type: str,
        hide_weekends: bool = False
    ) -> str:
    """
    Select the type of chart to display based on user input.
    """
    if chart_type == "Candlestick":
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

    elif chart_type == "Line":
        fig = go.Figure(data=[
            go.Scatter(
                x=df["Date"],
                y=df["Close"],
                mode="lines",
                name="Close Price"
            )
        ])
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price",
            height=500
        )
    else:
        st.error("Nieobsługiwany typ wykresu.")
        return None

    if hide_weekends:
        fig.update_xaxes(
            rangebreaks=[dict(bounds=["sat", "mon"])]
        )
    
    return fig


def stocks_data_page():
    """
    Main function to render the stocks data page.
    This function sets up the Streamlit page with controls and displays
    a candlestick chart and a data table for stock prices.
    """
    
    st.title("📈 Notowania spółek indeksu WIG20")

    # --- Top Controls ---
    col1, col2, col3 = st.columns(3)

    with col1:
        ticker = st.selectbox("Wybierz symbol:", WIG20_TICKERS)

        with st.expander("Opcje wykresu", expanded=True):
            col4, col5 = st.columns(2)
            
            with col4:
                # -- chart type ---
                chart_options = {
                    "Candlestick": "Świecowy",
                    "Line": "Liniowy"
                }
                chart_type = st.selectbox(
                    "Typ wykresu",
                    options=list(chart_options.keys()),
                    format_func=lambda x: chart_options[x]
                )

                hide_weekends = st.checkbox(
                    "Ukryj weekendy",
                    value=False,
                    help="Ukrywa dane z weekendów na wykresie."
                )
                
            with col5:
                timeframe_options = {
                    "Daily": "Dzienne",
                    "Hourly": "Godzinowe",
                }
                timeframe = st.selectbox(
                    "Zakres czaswoy świec",
                    options=list(timeframe_options.keys()),
                    format_func=lambda x: timeframe_options[x]
                )

    with col2:
        default_start_date = date(2025, 4, 1)
        default_end_date = date(2025, 4, 30)
        limit_start_date = date(2024, 1, 1)

        start_date = st.date_input(
            "Start Date", 
            value=default_start_date, 
            min_value=limit_start_date,
        )

    with col3:
        end_date = st.date_input(
            "End Date", 
            value=default_end_date,
            min_value=limit_start_date,
            )


    # --- load data ---
    data = select_dataset(timeframe)

    # --- validation ---
    if start_date > end_date:
        st.error(
            "🚫 Data początkowa zakresu musi być mniejsza od końcowej."
        )

    min_date = data["Date"].min().date()
    max_date = data["Date"].max().date()
    if start_date < min_date or end_date > max_date:
        st.error(
            f"🚫 Zakres dat musi być pomiędzy {min_date.strftime('%Y-%m-%d')}"
            f" a {max_date.strftime('%Y-%m-%d')}."
        )


    # --- filter ---
    df = filter_data(data, ticker, start_date, end_date)

    # --- charts ---
    left, right = st.columns([3, 2])

    with left:
        st.subheader("🕯️ Wykres Świecowy")

        if df.empty:
            st.warning("Brak danych dla wskazanego zakresu / symbolu.")
        else:
            fig = select_chart_type(df, chart_type, hide_weekends)
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


