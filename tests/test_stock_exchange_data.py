import pandas as pd
from datetime import datetime
from unittest.mock import patch
import os

from stock_exchange_data import process_stock_data
from stock_exchange_data import fetch_stock_data
from stock_exchange_data import fetch_example_wig20_data



def test_process_stock_data():
    raw_data = pd.DataFrame({
        ('Open', ''): [100],
        ('High', ''): [110],
        ('Low', ''): [95],
        ('Close', ''): [105],
        ('Volume', ''): [1000]
    }, index=pd.to_datetime(['2023-01-01']))

    raw_data.index.name = 'Date'

    result = process_stock_data("ABC", raw_data)

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ['Ticker', 'Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    assert result.iloc[0]['Ticker'] == 'ABC'


@patch("stock_exchange_data.yf.download")
def test_fetch_stock_data(mock_download):

    mock_data = pd.DataFrame({
        ('Open', ''): [100],
        ('High', ''): [110],
        ('Low', ''): [95],
        ('Close', ''): [105],
        ('Volume', ''): [1000]
    }, index=pd.to_datetime(['2023-01-01']))
    mock_data.index.name = 'Date'
    mock_download.return_value = mock_data

    start = datetime(2023, 1, 1)
    end = datetime(2023, 1, 10)
    tickers = ['ABC']

    df = fetch_stock_data(start, end, tickers)

    assert not df.empty
    assert list(df.columns) == ['Ticker', 'Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    assert pd.to_datetime(df.iloc[0]['Date']) == pd.Timestamp('2023-01-01')



@patch("stock_exchange_data.fetch_stock_data")
def test_fetch_example_wig20_data(mock_fetch):
    
    mock_fetch.return_value = pd.DataFrame([{
        'Ticker': 'ABC',
        'Date': '2023-01-01',
        'Close': 105,
        'High': 110,
        'Low': 95,
        'Open': 100,
        'Volume': 1000
    }])

    file_path = "tests/temp_output.csv"
    if os.path.exists(file_path):
        os.remove(file_path)

    fetch_example_wig20_data(file_path)

    assert os.path.exists(file_path)
    
    df = pd.read_csv(file_path)
    assert list(df.columns) == ['Ticker', 'Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    
    os.remove(file_path)  
