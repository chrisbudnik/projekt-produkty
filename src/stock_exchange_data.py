from typing import Dict, List
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


WIG20_TICKERS = [
    'PKN.WA',  # Orlen
    'PKO.WA',  # PKO Bank Polski
    'DNP.WA',  # Dino Polska
    'CDR.WA',  # CD Projekt
    'ALE.WA',  # Allegro.eu
    'KGH.WA',  # KGHM Polska Miedź
    'SPL.WA',  # Santander Bank Polska
    'PEO.WA',  # Bank Pekao
    'PZU.WA',  # PZU
    'MBK.WA',  # mBank
    'ALR.WA',  # Alior Bank
    'KRU.WA',  # Kruk
    'KTY.WA',  # Grupa Kęty
    'BDX.WA',  # Budimex
    'PGE.WA',  # PGE Polska Grupa Energetyczna
    'OPL.WA',  # Orange Polska
    'CPS.WA',  # Cyfrowy Polsat
    'PCO.WA',  # Pepco
    'JSW.WA',  # Jastrzębska Spółka Węglowa
    'LPP.WA'   # LPP
]


def process_stock_data(ticker: str, data: pd.DataFrame) -> pd.DataFrame:
    """Transform raw stock data from yfinance into a structured DataFrame."""

    df = data.copy()
    df.columns = df.columns.get_level_values(0) 
    df.reset_index(inplace=True)  
    df['Ticker'] = ticker 

    return df[['Ticker', 'Date', 'Close', 'High', 'Low', 'Open', 'Volume']]


def fetch_stock_data(date_from: datetime, date_to: datetime, tickers: List[str] = None) -> pd.DataFrame:
    """Fetch stock data for multiple tickers and return a combined DataFrame."""

    if not tickers:
        tickers = WIG20_TICKERS
    
    all_data = []
    for ticker in tickers:
        try:
            data = yf.download(
                ticker, 
                start=date_from.strftime('%Y-%m-%d'), 
                end=date_to.strftime('%Y-%m-%d')
            )
            processed_data = process_stock_data(ticker, data)
            all_data.append(processed_data)

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    
    return pd.concat(all_data, ignore_index=True)


def fetch_example_wig20_data(file_path: str, date_from: datetime = None, date_to: datetime = None) -> pd.DataFrame:
    """Fetch example WIG20 stock data for the last 30 days."""

    if not date_from and not date_to:
        date_to = datetime.today()
        date_from = date_to - timedelta(days=365)

    data = fetch_stock_data(date_from, date_to)

    with open(file_path, 'w') as f:
        data.to_csv(f, index=False)
    
    print(f"Example WIG20 data saved to `{file_path}`")



