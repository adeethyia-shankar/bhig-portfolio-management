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


def task1_stats_and_moves():
    "Task 1: Basic stats and biggest daily moves"
    print("\n📈 TASK 1: Stock Statistics & Biggest Daily Moves")

    # Ensure df and date column are available
    global df
    df = df.sort_values(["ticker", "date"], ascending=[True, True]).copy()

    # --- 1️⃣ Compute basic statistics for close prices ---
    stats = (
        df.groupby("ticker")["close"]
        .describe()[["mean", "std", "min", "max"]]
        .rename(columns={"mean": "avg_close", "std": "volatility"})
    )

    # --- 2️⃣ Compute daily % changes ---
    df["daily_return"] = (
        df.groupby("ticker")["close"].pct_change() * 100
    )  # in percent

    # --- 3️⃣ Find largest one-day % gains and losses per ticker ---
    biggest_moves = []
    for ticker, sub in df.groupby("ticker"):
        sub = sub.dropna(subset=["daily_return"])
        if sub.empty:
            continue
        max_gain = sub.loc[sub["daily_return"].idxmax()]
        max_loss = sub.loc[sub["daily_return"].idxmin()]
        biggest_moves.append({
            "ticker": ticker,
            "biggest_gain_date": max_gain["date"].strftime("%Y-%m-%d"),
            "biggest_gain_%": round(max_gain["daily_return"], 2),
            "biggest_loss_date": max_loss["date"].strftime("%Y-%m-%d"),
            "biggest_loss_%": round(max_loss["daily_return"], 2),
        })

    moves_df = pd.DataFrame(biggest_moves).set_index("ticker")

    # --- 4️⃣ Merge summary stats with moves ---
    summary = stats.join(moves_df, how="left")

    # --- 5️⃣ Save to CSV and display ---
    out_path = data_dir / "stock_stats_and_moves.csv"
    summary.to_csv(out_path)
    print(f"✅ Saved summary stats to {out_path}\n")
    print(summary.round(2))

    # --- 6️⃣ Plot daily returns histograms for each stock ---
    plots_dir = data_dir / "plots"
    plots_dir.mkdir(exist_ok=True)
    for ticker, sub in df.groupby("ticker"):
        if "daily_return" not in sub or sub["daily_return"].dropna().empty:
            continue
        plt.figure(figsize=(6, 3))
        plt.hist(sub["daily_return"].dropna(), bins=40, alpha=0.7, edgecolor="black")
        plt.title(f"{ticker} Daily Returns (%)")
        plt.xlabel("Daily Return (%)")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(plots_dir / f"{ticker}_daily_returns_hist.png", dpi=120)
        plt.close()
    print(f"✅ Daily return histograms saved to {plots_dir}")


    # TODO: group by ticker, use .describe() to get mean/std/min/max for close prices
    # TODO: calculate daily % change with .pct_change()
    # TODO: find largest single-day % gains and losses per stock
    # TODO: print formatted table showing stats + biggest moves
    pass
def task2_correlations():
    """Task 2: Correlation matrix and heatmap"""
    print("\n🤝 TASK 2: Stock Correlations")

    global df
    # Make sure daily returns exist (from task1). If not, compute them.
    if "daily_return" not in df.columns:
        df = df.sort_values(["ticker", "date"])
        df["daily_return"] = df.groupby("ticker")["close"].pct_change() * 100

    # --- 1️⃣ Pivot the data ---
    # We want each column to be a ticker, each row to be a date, and values = daily returns.
    pivot_df = df.pivot(index="date", columns="ticker", values="daily_return")

    # --- 2️⃣ Compute correlation matrix ---
    corr_matrix = pivot_df.corr()
    print("\n📊 Correlation matrix (rounded to 2 decimals):")
    print(corr_matrix.round(2))

    # --- 3️⃣ Plot heatmap ---
    import seaborn as sns
    plt.figure(figsize=(7, 5))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5,
        cbar_kws={"label": "Correlation"},
    )
    plt.title("Stock Daily Return Correlations")
    plt.tight_layout()

    # --- 4️⃣ Save the heatmap plot ---
    plots_dir = data_dir / "plots"
    plots_dir.mkdir(exist_ok=True)
    out_path = plots_dir / "correlation_heatmap.png"
    plt.savefig(out_path, dpi=120)
    plt.close()

    print(f"✅ Correlation heatmap saved to {out_path}")

    
    # TODO: pivot data so each column is a stock's daily returns
    # TODO: use .corr() to create 5x5 correlation matrices (AAPL vs MSFT, etc.)
    # TODO: use plt.imshow() or seaborn heatmap to visualize correlations
    # TODO: values near 1.0 = move together, near 0 = independent, near -1 = opposite
    pass

def task3_performance_volatility():
    """Task 3: Cumulative returns and volatility comparison"""
    print("\n📊 TASK 3: Performance & Volatility Analysis")

    global df
    df = df.sort_values(["ticker", "date"]).copy()

    # --- 1️⃣ Ensure daily returns exist ---
    if "daily_return" not in df.columns:
        df["daily_return"] = df.groupby("ticker")["close"].pct_change() * 100  # percent

    # --- 2️⃣ Compute cumulative returns ---
    # Convert % → decimal for compounding
    df["cum_return"] = (1 + df["daily_return"] / 100).groupby(df["ticker"]).cumprod()

    # --- 3️⃣ Plot cumulative returns (performance) ---
    plt.figure(figsize=(8, 4))
    for ticker, sub in df.groupby("ticker"):
        plt.plot(sub["date"], sub["cum_return"], label=ticker)
    plt.title("Cumulative Returns ($1 invested)")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.tight_layout()

    plots_dir = data_dir / "plots"
    plots_dir.mkdir(exist_ok=True)
    perf_path = plots_dir / "cumulative_returns.png"
    plt.savefig(perf_path, dpi=120)
    plt.close()
    print(f"✅ Cumulative return chart saved to {perf_path}")

    # --- 4️⃣ Compute rolling 30-day volatility (std of daily returns) ---
    df["rolling_volatility"] = (
        df.groupby("ticker")["daily_return"].rolling(30).std().reset_index(level=0, drop=True)
    )
    print("\nRolling 30-Day Volatility (last 10 days per stock):")
    for ticker, sub in df.groupby("ticker"):
        print(f"\n📌 {ticker}:")
        print(sub[["date", "rolling_volatility"]].tail(10).to_string(index=False))


    # --- 5️⃣ Plot rolling volatility ---
    plt.figure(figsize=(8, 4))
    for ticker, sub in df.groupby("ticker"):
        plt.plot(sub["date"], sub["rolling_volatility"], label=ticker)
    plt.title("30-Day Rolling Volatility (%)")
    plt.xlabel("Date")
    plt.ylabel("Volatility (Std of Daily % Returns)")
    plt.legend()
    plt.tight_layout()

    vol_path = plots_dir / "rolling_volatility.png"
    plt.savefig(vol_path, dpi=120)
    plt.close()
    print(f"✅ Rolling volatility chart saved to {vol_path}")

    print("📈 Performance and volatility comparison complete!\n")

    """Task 3: Cumulative returns and volatility comparison"""
    # TODO: calculate (1 + daily_returns).cumprod() for cumulative performance
    # TODO: plot line chart showing $1 invested in each stock over time
    # TODO: calculate .rolling(30).std() for 30-day volatility of returns
    # TODO: plot volatility comparison to see which stock is riskiest when
    pass

def task4_monthly_patterns():
    """Task 4: Monthly performance analysis"""
    print("\n📅 TASK 4: Monthly Patterns & Seasonality")

    global df
    df = df.sort_values(["ticker", "date"]).copy()

    # --- 1️⃣ Ensure daily returns exist ---
    if "daily_return" not in df.columns:
        df["daily_return"] = df.groupby("ticker")["close"].pct_change() * 100  # percent

    # --- 2️⃣ Extract month name and year-month ---
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")

    # --- 3️⃣ Compute average monthly return per stock ---
    monthly_avg = (
        df.groupby(["ticker", "month_name"])["daily_return"]
        .mean()
        .reset_index()
        .rename(columns={"daily_return": "avg_monthly_return"})
    )

    # Sort months in calendar order (Jan → Dec)
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_avg["month_name"] = pd.Categorical(monthly_avg["month_name"], categories=month_order, ordered=True)
    monthly_avg = monthly_avg.sort_values(["ticker", "month_name"])

    # --- 4️⃣ Plot average monthly returns ---
    plt.figure(figsize=(10, 5))
    for ticker, sub in monthly_avg.groupby("ticker"):
        plt.plot(sub["month_name"], sub["avg_monthly_return"], marker="o", label=ticker)

    plt.title("Average Monthly Returns by Stock")
    plt.xlabel("Month")
    plt.ylabel("Average Daily Return (%)")
    plt.legend(title="Ticker")
    plt.tight_layout()

    plots_dir = data_dir / "plots"
    plots_dir.mkdir(exist_ok=True)
    out_path = plots_dir / "monthly_patterns.png"
    plt.savefig(out_path, dpi=120)
    plt.close()

    print(f"✅ Monthly pattern chart saved to {out_path}")

    # --- 5️⃣ Save summary table for reference ---
    out_csv = data_dir / "monthly_avg_returns.csv"
    monthly_avg.to_csv(out_csv, index=False)
    print(f"✅ Monthly average returns saved to {out_csv}\n")

    print("📈 Seasonal pattern analysis complete — look for months where returns consistently spike!")

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
    task1_stats_and_moves()
    task2_correlations()
    task3_performance_volatility()
    task4_monthly_patterns()
    
    print("✅ Template ready - lightweight data exploration!")