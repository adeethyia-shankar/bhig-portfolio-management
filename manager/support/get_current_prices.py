"""
get_current_prices.py

Module for fetching live market prices for a portfolio of assets using Google Finance.

Reads a CSV-formatted portfolio file to extract tickers and exchange codes, then scrapes
the current price of each security from Google Finance.

Dependencies:
-------------
- yfinance

Author: Preetish Juneja, Adeethyia Shankar
Date: 2025-06-14
"""

import csv
from datetime import datetime
import yfinance as yf

def load_portfolio_stocks(file_path: str) -> list[tuple[str, str]]:
    """
    Load the list of tickers and exchanges from a portfolio CSV file.

    Parameters
    ----------
    file_path : str
        Path to the portfolio CSV file. Must contain 'ticker', 'exchange', and 'asset_name' columns.

    Returns
    -------
    list of tuple[str, str]
        A list of (ticker, exchange) pairs, excluding cash positions.
    """
    stocks = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["asset_name"] == 'Cash':
                continue
            stocks.append((row["ticker"], row['exchange']))
    return stocks

def get_current_prices(tickers: list[str]) -> dict[str, float]:
    """
    Fetch current stock prices from Yahoo Finance for a list of tickers.

    Parameters
    ----------
    tickers : list[str]
        List of tickers for which to fetch current prices.

    Returns
    -------
    dict
        Dictionary mapping each ticker to its most recent closing price (as a float).
        Example: { "AAPL": 189.44, "MSFT": 330.75 }
    
    Notes
    -----
    This function scrapes the "Previous close" field from each stock's Yahoo Finance page.
    """
    if not tickers:
        return dict()
    
    data = yf.download(tickers, period='1d', group_by='ticker', auto_adjust=True, progress=False)
    if data is None:
        raise RuntimeError('Could not fetch prices')
    prices = {
        ticker: data[ticker]['Close'].iloc[-1] for ticker in tickers
    }

    chf_to_usd = yf.Ticker('CHFUSD=X').info.get('previousClose', 0)
    for ticker in tickers:
        if ticker.endswith('.SW'):
            prices[ticker] *= chf_to_usd
    
    return prices

def get_prices(tickers: list[str], start_date: str, end_date: str) -> dict[datetime.date, dict[str, float]]:
    """
    Fetch historical open stock prices from Yahoo Finance for a list of tickers.

    Parameters
    ----------
    tickers : list[str]
        List of tickers for which to fetch historical prices.
    start_date : str
        Start date for the historical data in 'YYYY-MM-DD' format.
    end_date : str
        End date for the historical data in 'YYYY-MM-DD' format.

    Returns
    -------
    dict
        Dictionary mapping each date to its price DataFrame.
    """
    if not tickers:
        return dict()
    
    data = yf.download(tickers + ['CHFUSD=X'], start=start_date, end=end_date, auto_adjust=True, progress=False)
    if data is None:
        raise RuntimeError('Could not fetch prices')
    
    # Get the Open prices
    data_open = data['Open'].copy()
    
    # Convert Swiss franc prices to USD all at once
    swiss_tickers = [ticker for ticker in tickers if ticker.endswith('.SW')]
    if swiss_tickers:
        data_open[swiss_tickers] = data_open[swiss_tickers].multiply(data_open['CHFUSD=X'], axis=0)
    
    # Drop the exchange rate column and convert to dictionary
    data_open = data_open.drop(columns=['CHFUSD=X'])
    price_data = data_open.to_dict(orient='index')
    return price_data