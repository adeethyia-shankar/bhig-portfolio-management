"""
risk_metrics.py

Provides quantitative risk and attribution metrics for evaluating portfolio performance.
Includes volatility analysis, tracking error, value at risk, beta estimation, and
exposure to factor models such as Fama-French.

All metrics assume input returns are daily and may be benchmarked to an index (e.g., S&P Healthcare).

Dependencies
------------
- pandas
- scipy.stats
- statsmodels.api

Author: Preetish Juneja, Adeethyia Shankar
Date: 2025-06-14
"""

import pandas as pd
from scipy.stats import norm
import statsmodels.api as sm
from .constants import SQRT_252


def information_ratio(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Compute the information ratio (IR) relative to a benchmark.

    Parameters
    ----------
    portfolio_returns : pd.Series
        Series of portfolio returns.
    benchmark_returns : pd.Series
        Series of benchmark returns (e.g., sector ETF or index).

    Returns
    -------
    float
        Annualized information ratio: active return over active risk.
    """
    aligned = portfolio_returns.align(benchmark_returns, join='inner')
    rp, rb = aligned
    active_return = rp - rb
    return (active_return.mean() / active_return.std()) * SQRT_252


def rolling_information_ratio(portfolio_returns: pd.Series, benchmark_returns: pd.Series, window: int = 63) -> pd.Series:
    """
    Compute the rolling information ratio over a specified window.

    Parameters
    ----------
    portfolio_returns : pd.Series
        Daily portfolio returns.
    benchmark_returns : pd.Series
        Daily benchmark returns.
    window : int
        Rolling window size in days (default is 63 business days).

    Returns
    -------
    pd.Series
        Rolling information ratio.
    """
    aligned = portfolio_returns.align(benchmark_returns, join='inner')
    rp, rb = aligned
    active = rp - rb
    return active.rolling(window).mean() / active.rolling(window).std() * SQRT_252


def realized_volatility(returns: pd.Series, annualize: bool = True) -> float:
    """
    Compute realized volatility of a return series.

    Parameters
    ----------
    returns : pd.Series
        Daily return series.
    annualize : bool, optional
        Whether to scale volatility to an annualized value (default is True).

    Returns
    -------
    float
        Realized standard deviation (annualized if requested).
    """
    vol = returns.std()
    return vol * SQRT_252 if annualize else vol


def parametric_var(returns: pd.Series, alpha: float = 0.05) -> float:
    """
    Compute Value at Risk (VaR) using a parametric (Gaussian) model.

    Parameters
    ----------
    returns : pd.Series
        Daily return series.
    alpha : float
        Confidence level (e.g., 0.05 for 95% confidence).

    Returns
    -------
    float
        Parametric VaR value (loss is reported as positive).
    """
    mu = returns.mean()
    sigma = returns.std()
    z = float(norm.ppf(alpha))
    return -(mu + z * sigma)


def historical_var(returns: pd.Series, alpha: float = 0.05) -> float:
    """
    Compute historical Value at Risk (VaR) based on empirical distribution.

    Parameters
    ----------
    returns : pd.Series
        Daily return series.
    alpha : float
        Confidence level (default is 0.05 for 5%).

    Returns
    -------
    float
        Historical VaR (as a negative return).
    """
    return -returns.quantile(alpha)


def conditional_var(returns: pd.Series, alpha: float = 0.05) -> float:
    """
    Compute Conditional Value at Risk (CVaR), also known as Expected Shortfall.

    Parameters
    ----------
    returns : pd.Series
        Daily return series.
    alpha : float
        Confidence level (e.g., 0.05).

    Returns
    -------
    float
        Average loss in the worst alpha% of scenarios.
    """
    var_level = returns.quantile(alpha)
    return -returns[returns <= var_level].mean()


def beta_to_benchmark(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Estimate portfolio beta relative to a benchmark using linear regression.

    Parameters
    ----------
    portfolio_returns : pd.Series
        Series of portfolio returns.
    benchmark_returns : pd.Series
        Series of benchmark returns.

    Returns
    -------
    float
        Estimated beta coefficient.
    """
    aligned = portfolio_returns.align(benchmark_returns, join='inner')
    rp, rb = aligned
    X = sm.add_constant(rb)
    model = sm.OLS(rp, X).fit()
    return model.params[1]  # beta coefficient


def factor_exposures(portfolio_returns: pd.Series, factor_df: pd.DataFrame) -> pd.Series:
    """
    Estimate portfolio factor exposures using Fama-French 3-factor model.

    Parameters
    ----------
    portfolio_returns : pd.Series
        Daily portfolio returns.
    factor_df : pd.DataFrame
        DataFrame containing columns ['Mkt-RF', 'SMB', 'HML', 'RF'].

    Returns
    -------
    pd.Series
        Regression coefficients: alpha, market (Mkt-RF), SMB, HML exposures.
    """
    aligned = portfolio_returns.align(factor_df, join='inner')[0]
    excess = aligned - factor_df['RF']
    X = sm.add_constant(factor_df[['Mkt-RF', 'SMB', 'HML']])
    model = sm.OLS(excess, X).fit()
    return model.params


def tracking_error(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Compute annualized tracking error between portfolio and benchmark.

    Parameters
    ----------
    portfolio_returns : pd.Series
        Daily returns of the portfolio.
    benchmark_returns : pd.Series
        Daily returns of the benchmark.

    Returns
    -------
    float
        Annualized tracking error (standard deviation of active returns).
    """
    aligned = portfolio_returns.align(benchmark_returns, join='inner')
    active_return = aligned[0] - aligned[1]
    return active_return.std() * SQRT_252
