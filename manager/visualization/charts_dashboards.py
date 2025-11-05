"""
charts_dashboard.py

Streamlit dashboard for visualizing BHIG portfolio.

Displays:
- Portfolio-level total value and unrealized P&L
- Allocation breakdown by sector, asset class, or exchange (pie chart)

Author: Adeethyia Shankar
Date: 2025-10-07
"""

import streamlit as st
import pandas as pd
import plotly.express as px

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from daily import *
from manager.metrics.performance_metrics import *

# ---------------------------------------------------------------
# Load portfolio and prices
# ---------------------------------------------------------------
@st.cache_data
def load_portfolio_and_prices(bhig_portfolio: bool = True):
    """Load BHIG or mock portfolio and associated price map."""
    data_folder = DATA_FOLDER(bhig_portfolio)

    pf = load_portfolio_from_csv(portfolio_file(data_folder))
    current_prices = get_current_prices(pf.get_tickers())

    returns_df = pd.read_csv(returns_file(data_folder), header=None)
    returns_df.columns = [
        "date", "portfolio_value", "total_cash",
        "total_realized_pnl", "total_unrealized_pnl"
    ]
    returns_df["date"] = pd.to_datetime(returns_df["date"], errors="coerce")
    returns_df.drop_duplicates(subset=["date"], keep="last", inplace=True)
    returns_df.dropna(inplace=True)
    returns_df.reset_index(drop=True, inplace=True)

    return pf, current_prices, returns_df


# ---------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------

# Value metrics
def dashboard(portfolio: Portfolio, price_map: dict[str, float], returns_df: pd.DataFrame):
    total_val = portfolio.total_value(price_map)
    unrealized_pnl = portfolio.total_unrealized_pnl(price_map)
    cash_balance = portfolio.get_cash()

    st.subheader("💵 Portfolio Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Value", f"${total_val:,.2f}")
    col2.metric("Unrealized P&L", f"${unrealized_pnl:,.2f}")
    col3.metric("Cash Balance", f"${cash_balance:,.2f}")

    # Allocation visualization
    st.subheader("🎯 Allocation Breakdown")

    attribute = st.selectbox(
        "Choose allocation attribute:",
        ['ticker', "sector", "asset_class", "exchange"],
        index=0,
    )

    allocation = portfolio.allocation_by(attribute, price_map)

    if not allocation:
        st.warning("No allocation data found. Check if portfolio or prices are empty.")
    else:
        alloc_df = pd.DataFrame(list(allocation.items()), columns=[attribute.capitalize(), "Weight"])
        alloc_df["Weight (%)"] = alloc_df["Weight"] * 100

        fig = px.pie(
            alloc_df,
            values="Weight",
            names=attribute.capitalize(),
            title=f"Portfolio Allocation by {attribute.capitalize()}",
            hole=0.4,
        )
        st.plotly_chart(fig)

        st.dataframe(alloc_df.style.format({"Weight": "{:.2%}", "Weight (%)": "{:.2f}"}))
    
    # --- Portfolio performance ---
    st.subheader("📈 Portfolio Performance Over Time")

    try:
        # Line chart
        fig2 = px.line(
            returns_df,
            x="date",
            y="portfolio_value",
            labels={'date': 'Date', 'portfolio_value': 'Portfolio Value ($)'}
        )
        st.plotly_chart(fig2)

        # Compute metrics from performance_metrics.py
        returns = get_returns(returns_df)
        
        metrics = {
            "Total Return": f"{total_return(returns) * 100:.2f}%",
            # "CAGR": f"{cagr(returns) * 100:.2f}%",
            "Sharpe Ratio": f"{sharpe_ratio(returns):.2f}"
            # "Sortino Ratio": f"{sortino_ratio(returns):.2f}",
            # "Max Drawdown": f"{max_drawdown(returns) * 100:.2f}%",
        }

        # Display metrics
        st.subheader("📊 Metrics")
        cols = st.columns(len(metrics))
        for i, (k, v) in enumerate(metrics.items()):
            cols[i].metric(k, v)

    except FileNotFoundError:
        st.warning("⚠️ No returns.csv file found — performance metrics unavailable.")
    except Exception as e:
        st.error(f"Error reading performance data: {e}")

st.set_page_config(page_title="BHIG Portfolio Allocation", layout="wide")

st.image('BHIG.jpg')

st.title("Brown Healthcare Investing Group — Portfolio Dashboard")

# Portfolio selector
portfolio_choice = st.radio("Select Portfolio", ["BHIG Portfolio", "Mock Portfolio"])
bhig_portfolio = portfolio_choice == "BHIG Portfolio"

# Load data
with st.spinner("Loading portfolio and prices..."):
    dashboard(*load_portfolio_and_prices(bhig_portfolio))
