# backtester/signal_generator.py
# =============== 11/11 WEEK ASSIGNMENT ======================
# ===============     SIGNAL GENERATION   ====================

# Goal: Create and visualize basic trading signals
# Focus: Turn your data exploration insights into quantifiable indicators
# Future: These signals will feed into the backtester next week (Week 4)

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# ==========================================================
# 0. Load cleaned data
# ----------------------------------------------------------
data_dir = Path("data")
clean_data_path = data_dir / "clean_prices.csv"

if not clean_data_path.exists():
    print("❌ Run dataloader.py first to generate clean_prices.csv")
    exit(1)

df = pd.read_csv(clean_data_path)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["ticker", "date"])

print("📊 Loaded cleaned price data for signal generation...\n")

# ==========================================================
# TODO: Signal Generation (Week 3) - 5 Tasks
# ----------------------------------------------------------
# Goal: Turn data exploration insights into quantifiable trading signals
# Future: These signals will drive buy/sell decisions in the backtester

# 1. Momentum Signal
#    calculate percent change over lookback period (e.g., 20 days)
#    → BUY when momentum is positive (trending up)
#    → SELL when momentum is negative (trending down)

# 2. Mean Reversion Signal (Z-Score)
#    measure how far price is from its rolling average
#    → BUY when z-score is very negative (price unusually low)
#    → SELL when z-score is very positive (price unusually high)

# 3. Volatility Signal
#    calculate rolling standard deviation of daily returns
#    → HIGH volatility = more risk, bigger potential moves
#    → LOW volatility = more stable, smaller moves

# 4. Volume Spike Signal
#    ratio of current volume to rolling average volume
#    → volume spike + price up = strong buying pressure
#    → volume spike + price down = panic selling

# 5. Sharpe Ratio
#    risk-adjusted returns (return / volatility)
#    → higher sharpe = better returns for the risk taken
#    → prefer stocks with sharpe > 1.0

# ==========================================================


def signal_momentum(df, lookback=20):
    """Task 1: Momentum signal - trend following"""
    # TODO: use .pct_change(periods=lookback) to calculate momentum
    # TODO: group by ticker so each stock calculated separately
    # TODO: store result in column named f"momentum_{lookback}"
    # TODO: positive values = upward trend, negative = downward trend
    pass

def signal_mean_reversion(df, window=20):
    """Task 2: Mean reversion signal - buy low, sell high"""
    # TODO: calculate rolling mean of price with .rolling(window).mean()
    # TODO: calculate rolling std with .rolling(window).std()
    # TODO: compute z-score = (price - rolling_mean) / rolling_std
    # TODO: z-score shows how many standard deviations away from average
    # TODO: store in column named f"zscore_{window}"
    pass

def signal_volatility(df, window=30):
    """Task 3: Volatility signal - measure risk/uncertainty"""
    # TODO: first calculate daily returns with .pct_change()
    # TODO: then calculate .rolling(window).std() of those returns
    # TODO: group by ticker for per-stock volatility
    # TODO: higher values = more volatile/risky, lower = more stable
    # TODO: store in column named f"volatility_{window}"
    pass

def signal_volume_spike(df, window=20):
    """Task 4: Volume spike signal - detect unusual activity"""
    # TODO: calculate rolling average of volume with .rolling(window).mean()
    # TODO: divide current volume by rolling average
    # TODO: ratio > 1.0 = above average volume
    # TODO: ratio > 2.0 = significant spike (something happening!)
    # TODO: store in column named f"volume_ratio_{window}"
    pass

def signal_sharpe_ratio(df, window=30):
    """Task 5: Sharpe ratio - risk-adjusted returns"""
    # TODO: calculate daily returns with .pct_change()
    # TODO: calculate rolling mean of returns
    # TODO: calculate rolling std of returns
    # TODO: sharpe = (mean_return / std_return) * sqrt(252)
    # TODO: multiply by sqrt(252) to annualize
    # TODO: store in column named "rolling_sharpe"
    pass

def visualize_signals(df, ticker="AAPL"):
    """Task 6: Visualization - plot all signals for one stock"""
    # TODO: filter df for single ticker
    # TODO: create figure with 3 subplots (price, signals, risk metrics)
    # TODO: plot 1: price over time
    # TODO: plot 2: momentum and z-score signals
    # TODO: plot 3: sharpe ratio and volatility
    # TODO: add labels, legends, and grid
    # TODO: save to data/plots/{ticker}_signals.png
    pass

def summarize_signals(df):
    """Task 7: Summary statistics and save to CSV"""
    # TODO: select signal columns (momentum_20, zscore_20, etc.)
    # TODO: use .describe() to show mean, std, min, max for each signal
    # TODO: save full dataframe with all signals to data/signals.csv
    # TODO: print confirmation message with file path
    pass

# ==========================================================
# Main Execution
# ----------------------------------------------------------
if __name__ == "__main__":
    print("🎯 Week 3: Signal Generator - Turning Data into Signals")
    print("📚 Goal: Quantify behavior like momentum, reversion, risk")
    print("💡 Future: Feed into strategy tester for entry/exit rules\n")
    
    print("📝 Complete these 7 tasks:")
    print("   1. Momentum Signal")
    print("   2. Mean Reversion Signal")
    print("   3. Volatility Signal")
    print("   4. Volume Spike Signal")
    print("   5. Sharpe Ratio Signal")
    print("   6. Visualization")
    print("   7. Summary & Save\n")

    # TODO: uncomment as you complete each task
    # df = signal_momentum(df, lookback=20)
    # df = signal_mean_reversion(df, window=20)
    # df = signal_volatility(df, window=30)
    # df = signal_volume_spike(df, window=20)
    # df = signal_sharpe_ratio(df, window=30)
    # summarize_signals(df)
    # visualize_signals(df, ticker="AAPL")

    print("✅ Template ready - time to build your trading signals!")
