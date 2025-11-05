# backtester/data_explorer.py
# =============== 11/4 WEEK ASSIGNMENT ======================
# ===============    BOILERPLATE CODE  ======================

# Goal: Explore and understand the cleaned data from dataloader.py
# Focus: Data analysis fundamentals before moving to trading strategies
# Light workload with detailed explanations for learning

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Load cleaned data from previous week's work
data_dir = Path("data")
clean_data_path = data_dir / "clean_prices.csv"

if not clean_data_path.exists():
    print("❌ Run dataloader.py first to generate clean_prices.csv")
    exit(1)

print("📊 Loading cleaned price data for exploration...")
df = pd.read_csv(clean_data_path)
df["date"] = pd.to_datetime(df["date"])

# ==========================================================
# TODO: Data Exploration (Week 2) - 4 Tasks
# ----------------------------------------------------------
# Goal: Basic data analysis before building strategies
# Future: These analyses Could become trading signals later

# 1. Stock Statistics & Daily Moves
#    calculate basic stats (mean, std) and find biggest daily moves
#    → FUTURE SIGNAL: mean reversion (buy when price far below average)

# 2. Stock Correlations  
#    correlation matrix and heatmap - which stocks move together
#    → FUTURE SIGNAL: pairs trading (when correlated stocks diverge)

# 3. Performance & Volatility
#    cumulative returns and rolling volatility comparison
#    → FUTURE SIGNAL: momentum (buy stocks accelerating returns) / breakouts (buy when volatility spikes)

# 4. Monthly Patterns
#    average returns by month for seasonal analysis
#    → FUTURE SIGNAL: seasonal trading (buy in historically good months)

# 5. (Optional) create own potential signal, could be anything quantifiable that we can trade on
# examples: volume spikes, sharpe ratio instead of returns, skew, etc.


# ==========================================================


def task1_stats_and_moves():
    """Task 1: Basic stats and biggest daily moves"""
    # TODO: group by ticker, use .describe() to get mean/std/min/max for close prices
    # TODO: calculate daily % change with .pct_change()
    # TODO: find largest single-day % gains and losses per stock
    # TODO: print formatted table showing stats + biggest moves
    pass

def task2_correlations():
    """Task 2: Correlation matrix and heatmap"""
    # TODO: pivot data so each column is a stock's daily returns
    # TODO: use .corr() to create 5x5 correlation matrices (AAPL vs MSFT, etc.)
    # TODO: use plt.imshow() or seaborn heatmap to visualize correlations
    # TODO: values near 1.0 = move together, near 0 = independent, near -1 = opposite
    pass

def task3_performance_volatility():
    """Task 3: Cumulative returns and volatility comparison"""
    # TODO: calculate (1 + daily_returns).cumprod() for cumulative performance
    # TODO: plot line chart showing $1 invested in each stock over time
    # TODO: calculate .rolling(30).std() for 30-day volatility of returns
    # TODO: plot volatility comparison to see which stock is riskiest when
    pass

def task4_monthly_patterns():
    """Task 4: Monthly performance analysis"""
    # TODO: extract month from date, group returns by ticker and month
    # TODO: calculate .mean() returns for each stock in each month
    # TODO: create bar chart with months on x-axis, avg return on y-axis
    # TODO: separate bars/colors for each stock to compare seasonal patterns
    pass

# Simple main execution
if __name__ == "__main__":
    print("🎯 Week 2: Data Explorer - Understanding Your Stock Data")
    print("📚 Goal: Learn about your data before building strategies")
    print("🎨 Focus: Statistics, correlations, trends, patterns")
    print("💡 No trading yet - just understanding what you're working with!\n")
    
    print("📝 Complete these 4 tasks:")
    print("   1. Stats & Daily Moves")
    print("   2. Correlations")
    print("   3. Performance & Volatility")
    print("   4. Monthly Patterns\n")
    
    # Uncomment as you complete:
    # task1_stats_and_moves()
    # task2_correlations()
    # task3_performance_volatility()
    # task4_monthly_patterns()
    
    print("✅ Template ready - lightweight data exploration!")