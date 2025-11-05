from base.portfolio import *
from metrics.constants import BUSINESS_DAYS_PER_YEAR
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def simulate_equity_price_shock(portfolio: Portfolio, price_map: dict[str, float], shocks: dict[str, float]) -> dict:
    """
    Simulates price shocks for specific tickers and returns portfolio-level impact.

    Parameters
    ----------
    portfolio : Portfolio
        A Portfolio object containing positions and metadata.
    price_map : dict[str, float]
        A dictionary mapping tickers to their current prices.
    shocks : dict[str, float]
        A dictionary mapping tickers to shock percentages (e.g., {"AAPL": -0.2} for a 20% drop).

    Returns
    -------
    dict
        A dictionary with total original and shocked value, total delta, percentage delta,
        and ticker-level P&L contributions.
    """
    results = []
    original_value = portfolio.total_value(price_map)

    for ticker, position in portfolio.positions.items():
        if ticker not in price_map:
            continue
        current_price = price_map[ticker]
        shock = shocks.get(ticker, 0.0)
        shocked_price = current_price * (1 + shock)

        position_value_now = position.quantity * current_price
        position_value_after = position.quantity * shocked_price
        pnl_change = position_value_after - position_value_now

        results.append({
            "ticker": ticker,
            "current_price": current_price,
            "shocked_price": shocked_price,
            "pnl_change": pnl_change,
            "pnl_change_pct": pnl_change / original_value * 100
        })

    shocked_value = original_value + sum(r["pnl_change"] for r in results)

    return {
        "original_value": original_value,
        "shocked_value": shocked_value,
        "delta": shocked_value - original_value,
        "delta_pct": (shocked_value - original_value) / original_value * 100,
        "details": results
    }

def plot_equity_shock_results(results: dict):
    """
    Plots the equity shock results using a bar chart and prints summary stats.

    Parameters
    ----------
    results : dict
        Output dictionary from simulate_equity_price_shock().

    Returns
    -------
    None
    """
    df = pd.DataFrame(results["details"])
    df.set_index("ticker", inplace=True)

    ax = df["pnl_change"].plot(kind="bar", figsize=(10, 5), title="Equity Price Shock Impact by Ticker")
    ax.axhline(0, color='black', linewidth=0.8)
    plt.ylabel("P&L Impact ($)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

    print(f"Original Portfolio Value: ${results['original_value']:.2f}")
    print(f"Shocked Portfolio Value: ${results['shocked_value']:.2f}")
    print(f"Change: ${results['delta']:.2f} ({results['delta_pct']:.2f}%)")

def apply_sector_shock(portfolio: Portfolio, price_map: dict[str, float], sector_shocks: dict[str, float]) -> dict:
    """
    Simulates a sector-based shock, applying uniform changes to all assets in a sector.

    Parameters
    ----------
    portfolio : Portfolio
        The portfolio with sector-labeled positions.
    price_map : dict[str, float]
        Current prices for tickers.
    sector_shocks : dict[str, float]
        Shock per sector (e.g., {"Technology": -0.10}).

    Returns
    -------
    dict
        Output from simulate_equity_price_shock().
    """
    ticker_shocks = {
        ticker: sector_shocks.get(pos.sector, 0.0)
        for ticker, pos in portfolio.positions.items()
    }
    return simulate_equity_price_shock(portfolio, price_map, ticker_shocks)

def apply_correlated_shocks(portfolio: Portfolio, price_map: dict[str, float], cov_matrix: pd.DataFrame,
                            mean_shock: float = 0.0, std_shock: float = 0.02, random_state: int = 42) -> dict:
    """
    Simulates a correlated shock using a multivariate normal distribution based on return covariance.

    Parameters
    ----------
    portfolio : Portfolio
    price_map : dict[str, float]
    cov_matrix : pd.DataFrame
        Covariance matrix of returns.
    mean_shock : float
        Mean expected shock for simulation.
    std_shock : float
        Std deviation multiplier for shock magnitude.
    random_state : int
        Seed for reproducibility.

    Returns
    -------
    dict
        Output from simulate_equity_price_shock().
    """
    np.random.seed(random_state)
    tickers = [t for t in portfolio.positions if t in cov_matrix.columns]
    cov = cov_matrix.loc[tickers, tickers]
    shocks = np.random.multivariate_normal(mean=[mean_shock] * len(tickers), cov=cov * (std_shock**2))
    ticker_shocks = {ticker: shock for ticker, shock in zip(tickers, shocks)}
    return simulate_equity_price_shock(portfolio, price_map, ticker_shocks)

def apply_multi_asset_shock(portfolio: Portfolio, price_map: dict[str, float],
                            equity_shocks: dict[str, float], fx_shocks: dict[str, float]) -> dict:
    """
    Applies asset-class-specific shocks to the portfolio.

    Parameters
    ----------
    portfolio : Portfolio
    price_map : dict[str, float]
    equity_shocks : dict[str, float]
    fx_shocks : dict[str, float]

    Returns
    -------
    dict
        Output from simulate_equity_price_shock().
    """
    ticker_shocks = {}
    for ticker, pos in portfolio.positions.items():
        if pos.asset_class == "Equity":
            ticker_shocks[ticker] = equity_shocks.get(ticker, 0.0)
        elif pos.asset_class == "FX":
            ticker_shocks[ticker] = fx_shocks.get(ticker, 0.0)
    return simulate_equity_price_shock(portfolio, price_map, ticker_shocks)

def apply_factor_based_shock(portfolio: Portfolio, price_map: dict[str, float],
                             factor_shocks: dict[str, float], factor_loadings: pd.DataFrame) -> dict:
    """
    Simulates portfolio impact of a macro/factor model shock (e.g., Fama-French factors).

    Parameters
    ----------
    portfolio : Portfolio
    price_map : dict[str, float]
    factor_shocks : dict[str, float]
        e.g., {"Mkt-RF": -0.02, "SMB": 0.01}
    factor_loadings : pd.DataFrame
        DataFrame indexed by ticker with factor loadings as columns.

    Returns
    -------
    dict
        Output from simulate_equity_price_shock().
    """
    tickers = list(portfolio.positions.keys())
    relevant_loadings = factor_loadings.loc[tickers]
    shocks_series = pd.Series(factor_shocks)
    ticker_shocks = relevant_loadings.dot(shocks_series).to_dict()
    return simulate_equity_price_shock(portfolio, price_map, ticker_shocks)

def monte_carlo_simulation(portfolio: Portfolio, price_map: dict[str, float],
                           mu: dict[str, float], sigma: dict[str, float],
                           days: int = 252, n_sim: int = 1000, random_state: int = 42) -> pd.DataFrame:
    """
    Runs Monte Carlo simulations for GBM-driven asset price paths and returns portfolio trajectories.

    Parameters
    ----------
    portfolio : Portfolio
    price_map : dict[str, float]
    mu : dict[str, float]
        Expected annual return per ticker.
    sigma : dict[str, float]
        Annualized volatility per ticker.
    days : int
        Number of trading days to simulate.
    n_sim : int
        Number of simulations to run.
    random_state : int
        Seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        DataFrame of shape (n_sim, days) containing simulated portfolio values.
    """
    np.random.seed(random_state)
    tickers = list(portfolio.positions.keys())
    dt = 1 / BUSINESS_DAYS_PER_YEAR
    sim_results = np.zeros((n_sim, days))

    for i in range(n_sim):
        sim_price_map = price_map.copy()
        port_vals = []

        for t in range(days):
            for ticker in tickers:
                drift = (mu[ticker] - 0.5 * sigma[ticker] ** 2) * dt
                shock = sigma[ticker] * np.random.normal() * np.sqrt(dt)
                sim_price_map[ticker] *= np.exp(drift + shock)
            value = portfolio.total_value(sim_price_map)
            port_vals.append(value)

        sim_results[i, :] = port_vals

    return pd.DataFrame(sim_results)
