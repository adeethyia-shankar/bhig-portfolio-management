"""
performance_metrics.py

Provides financial performance metrics for portfolio evaluation, including return
calculations, risk-adjusted ratios (Sharpe, Sortino), drawdown analysis, and IRR-based
performance measures.

Supports both point-in-time metrics and rolling window analytics for backtesting and
portfolio monitoring.

Dependencies
------------
- NumPy
- Pandas
- SciPy
- base.portfolio
- metrics.constants

Author: Preetish Juneja, Adeethyia Shankar
Date: 2025-06-14
"""

import numpy as np
import pandas as pd
from datetime import datetime
from scipy.optimize import newton
from manager.base.portfolio import Portfolio
from .constants import BUSINESS_DAYS_PER_YEAR, SQRT_252, DAYS_PER_YEAR


def get_returns(returns_df: pd.DataFrame) -> pd.Series:
    """
    Load a portfolio value CSV and compute daily returns.

    Parameters
    ----------
    returns_df : pd.DataFrame
        DataFrame with columns ['date', 'portfolio_value'].

    Returns
    -------
    pd.Series
        Time series of daily returns indexed by datetime.
    """
    # Set the date as index first
    returns_df = returns_df.set_index('date')
    # Calculate returns
    returns = returns_df['portfolio_value'].pct_change(fill_method=None)
    # Drop the first NaN value that results from pct_change()
    returns = returns.dropna()
    return returns


def total_return(returns: pd.Series) -> float:
    """
    Calculate total cumulative return.

    Parameters
    ----------
    returns : pd.Series
        Series of daily returns.

    Returns
    -------
    float
        Total return over the full time horizon.
    """
    return (1 + returns).prod() - 1


def cagr(returns: pd.Series) -> float:
    """
    Calculate compound annual growth rate (CAGR).

    Parameters
    ----------
    returns : pd.Series
        Series of daily returns.

    Returns
    -------
    float
        CAGR annualized over the full period.
    """
    total_ret = total_return(returns)
    n_years = (returns.index[-1] - returns.index[0]).days / DAYS_PER_YEAR
    return ((1 + total_ret) ** (1 / n_years)) - 1


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate annualized Sharpe ratio.

    Parameters
    ----------
    returns : pd.Series
        Series of daily returns.
    risk_free_rate : float, optional
        Annualized risk-free rate (default is 0.0).

    Returns
    -------
    float
        Sharpe ratio based on excess returns.
    """
    excess = returns - (risk_free_rate / BUSINESS_DAYS_PER_YEAR)
    return (np.mean(excess) / np.std(excess)) * SQRT_252


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate annualized Sortino ratio.

    Parameters
    ----------
    returns : pd.Series
        Series of daily returns.
    risk_free_rate : float, optional
        Annualized risk-free rate (default is 0.0).

    Returns
    -------
    float
        Sortino ratio using downside deviation.
    """
    excess = returns - (risk_free_rate / BUSINESS_DAYS_PER_YEAR)
    downside = np.std(excess[excess < 0])
    return (np.mean(excess) / downside) * SQRT_252 if downside > 0 else np.nan


def max_drawdown(returns: pd.Series) -> float:
    """
    Calculate the maximum drawdown.

    Parameters
    ----------
    returns : pd.Series
        Series of daily returns.

    Returns
    -------
    float
        Largest peak-to-trough decline as a negative percentage.
    """
    cumulative = (1 + returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return drawdown.min()


def time_weighted_return(returns: pd.Series) -> float:
    """
    Compute the time-weighted rate of return (TWRR).

    Parameters
    ----------
    returns : pd.Series
        Series of daily returns.

    Returns
    -------
    float
        Time-weighted return.
    """
    return (1 + returns).prod() - 1


def money_weighted_return(portfolio: Portfolio, price_map: dict[str, float]) -> float:
    """
    Calculate the internal rate of return (IRR), also known as money-weighted return.

    Parameters
    ----------
    portfolio : Portfolio
        The portfolio object containing positions and transactions.
    price_map : dict[str, float]
        Dictionary of current prices for each asset in the portfolio.

    Returns
    -------
    float
        IRR computed via numerical optimization of net present value.
    """
    cash_flows = []

    for position in portfolio.positions.values():
        for txn in position.transactions:
            cash_flow = (txn.quantity * txn.price) + txn.fees
            cash_flows.append((txn.date, cash_flow))

    if not cash_flows:
        return float("nan")

    today = max([date for date, _ in cash_flows] + [datetime.today()])
    terminal_value = portfolio.total_value(price_map)
    cash_flows.append((today, terminal_value))

    cash_flows.sort()
    start_date = cash_flows[0][0]

    times = [(date - start_date).days / DAYS_PER_YEAR for date, _ in cash_flows]
    values = [cf for _, cf in cash_flows]

    def npv(rate):
        return sum(cf / (1 + rate) ** t for cf, t in zip(values, times))

    try:
        irr = newton(npv, 0.10)
        return float(irr)
    except RuntimeError:
        return float("nan")


def rolling_sharpe(returns: pd.Series, risk_free_rate: float = 0.0, window: int = 63) -> pd.Series:
    """
    Compute the rolling Sharpe ratio over a given window.

    Parameters
    ----------
    returns : pd.Series
        Series of daily returns.
    risk_free_rate : float, optional
        Annualized risk-free rate (default is 0.0).
    window : int, optional
        Rolling window size in days (default is 63 trading days).

    Returns
    -------
    pd.Series
        Time series of rolling Sharpe ratios.
    """
    excess = returns - (risk_free_rate / BUSINESS_DAYS_PER_YEAR)
    rolling_mean = excess.rolling(window=window).mean()
    rolling_std = excess.rolling(window=window).std()
    return (rolling_mean / rolling_std) * SQRT_252


def rolling_max_drawdown(returns: pd.Series, window: int = BUSINESS_DAYS_PER_YEAR) -> pd.Series:
    """
    Compute rolling maximum drawdown over a fixed window.

    Parameters
    ----------
    returns : pd.Series
        Series of daily returns.
    window : int, optional
        Rolling window size (default is one business year).

    Returns
    -------
    pd.Series
        Time series of max drawdown values.
    """
    cumulative = (1 + returns).cumprod()
    rolling = cumulative.rolling(window)
    return rolling.apply(lambda x: (x / x.cummax()).min() - 1, raw=False)
