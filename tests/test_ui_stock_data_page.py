import pandas as pd
from ui.stocks_data_page import filter_data


def test_filter_data():
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2023-01-01", "2023-01-05", "2023-01-10"]),
        "Ticker": ["ABC", "XYZ", "ABC"],
        "Close": [100, 200, 150]
    })

    filtered = filter_data(df, "ABC", "2023-01-01", "2023-01-10")

    assert (filtered["Ticker"] == "ABC").all()
    assert filtered["Date"].min() >= pd.Timestamp("2023-01-01")
    assert filtered["Date"].max() <= pd.Timestamp("2023-01-10")
