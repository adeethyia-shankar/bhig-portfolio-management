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
    
    print("\n" + "="*60)
    print("task 1: stock statistics & daily moves")
    print("="*60)
    
    # basic stats per stock
    stats = df.groupby('ticker')['close'].describe()[['mean', 'std', 'min', 'max']]
    print("\nprice statistics:")
    print(stats.round(2))
    
    # calculate daily returns
    df_sorted = df.sort_values(['ticker', 'date'])
    df_sorted['daily_return'] = df_sorted.groupby('ticker')['close'].pct_change() * 100
    
    # find biggest moves per stock
    print("\nbiggest single-day moves:")
    for ticker in df['ticker'].unique():
        ticker_data = df_sorted[df_sorted['ticker'] == ticker].copy()
        max_gain = ticker_data.loc[ticker_data['daily_return'].idxmax()]
        max_loss = ticker_data.loc[ticker_data['daily_return'].idxmin()]
        
        print(f"\n{ticker}:")
        print(f"  largest gain:  {max_gain['daily_return']:.2f}% on {max_gain['date'].strftime('%Y-%m-%d')}")
        print(f"  largest loss:  {max_loss['daily_return']:.2f}% on {max_loss['date'].strftime('%Y-%m-%d')}")

def task2_correlations():
    """Task 2: Correlation matrix and heatmap"""
    # TODO: pivot data so each column is a stock's daily returns
    # TODO: use .corr() to create 5x5 correlation matrices (AAPL vs MSFT, etc.)
    # TODO: use plt.imshow() or seaborn heatmap to visualize correlations
    # TODO: values near 1.0 = move together, near 0 = independent, near -1 = opposite
    
    print("\n" + "="*60)
    print("task 2: stock correlations")
    print("="*60)
    
    # calculate daily returns
    df_sorted = df.sort_values(['ticker', 'date'])
    df_sorted['daily_return'] = df_sorted.groupby('ticker')['close'].pct_change()
    
    # pivot to get each stock as a column
    returns_pivot = df_sorted.pivot(index='date', columns='ticker', values='daily_return')
    
    # calculate correlation matrix
    corr_matrix = returns_pivot.corr()
    print("\ncorrelation matrix:")
    print(corr_matrix.round(3))
    
    # create heatmap
    plt.figure(figsize=(10, 8))
    plt.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
    plt.colorbar(label='correlation')
    plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=45)
    plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
    plt.title('stock correlation heatmap')
    
    # add correlation values to cells
    for i in range(len(corr_matrix.columns)):
        for j in range(len(corr_matrix.columns)):
            plt.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                    ha='center', va='center', color='black', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(data_dir / 'plots' / 'correlation_heatmap.png')
    print(f"\n✅ heatmap saved to {data_dir / 'plots' / 'correlation_heatmap.png'}")
    plt.close()

def task3_performance_volatility():
    """Task 3: Cumulative returns and volatility comparison"""
    # TODO: calculate (1 + daily_returns).cumprod() for cumulative performance
    # TODO: plot line chart showing $1 invested in each stock over time
    # TODO: calculate .rolling(30).std() for 30-day volatility of returns
    # TODO: plot volatility comparison to see which stock is riskiest when
    
    print("\n" + "="*60)
    print("task 3: performance & volatility")
    print("="*60)
    
    # calculate daily returns
    df_sorted = df.sort_values(['ticker', 'date'])
    df_sorted['daily_return'] = df_sorted.groupby('ticker')['close'].pct_change()
    
    # pivot for easier calculation
    returns_pivot = df_sorted.pivot(index='date', columns='ticker', values='daily_return')
    
    # cumulative returns (growth of $1)
    cumulative_returns = (1 + returns_pivot).cumprod()
    
    # plot cumulative performance
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    for ticker in cumulative_returns.columns:
        plt.plot(cumulative_returns.index, cumulative_returns[ticker], label=ticker)
    plt.title('cumulative returns ($1 invested)')
    plt.xlabel('date')
    plt.ylabel('portfolio value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # calculate 30-day rolling volatility
    rolling_volatility = returns_pivot.rolling(window=30).std() * np.sqrt(252) * 100
    
    # plot volatility
    plt.subplot(1, 2, 2)
    for ticker in rolling_volatility.columns:
        plt.plot(rolling_volatility.index, rolling_volatility[ticker], label=ticker)
    plt.title('30-day rolling volatility (annualized %)')
    plt.xlabel('date')
    plt.ylabel('volatility %')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(data_dir / 'plots' / 'performance_volatility.png')
    print(f"\n✅ charts saved to {data_dir / 'plots' / 'performance_volatility.png'}")
    plt.close()
    
    # print final returns
    final_returns = (cumulative_returns.iloc[-1] - 1) * 100
    print("\ntotal returns over period:")
    for ticker in final_returns.index:
        print(f"  {ticker}: {final_returns[ticker]:.2f}%")

def task4_monthly_patterns():
    """Task 4: Monthly performance analysis"""
    # TODO: extract month from date, group returns by ticker and month
    # TODO: calculate .mean() returns for each stock in each month
    # TODO: create bar chart with months on x-axis, avg return on y-axis
    # TODO: separate bars/colors for each stock to compare seasonal patterns
    
    print("\n" + "="*60)
    print("task 4: monthly patterns")
    print("="*60)
    
    # calculate daily returns
    df_sorted = df.sort_values(['ticker', 'date'])
    df_sorted['daily_return'] = df_sorted.groupby('ticker')['close'].pct_change() * 100
    
    # extract month
    df_sorted['month'] = df_sorted['date'].dt.month
    
    # calculate average returns by ticker and month
    monthly_avg = df_sorted.groupby(['ticker', 'month'])['daily_return'].mean().reset_index()
    monthly_pivot = monthly_avg.pivot(index='month', columns='ticker', values='daily_return')
    
    print("\naverage daily return by month (%):")
    print(monthly_pivot.round(3))
    
    # create bar chart
    plt.figure(figsize=(12, 6))
    x = np.arange(1, 13)
    width = 0.15
    tickers = monthly_pivot.columns
    
    for i, ticker in enumerate(tickers):
        offset = (i - len(tickers)/2 + 0.5) * width
        values = [monthly_pivot.loc[m, ticker] if m in monthly_pivot.index else 0 for m in range(1, 13)]
        plt.bar(x + offset, values, width, label=ticker)
    
    plt.xlabel('month')
    plt.ylabel('average daily return (%)')
    plt.title('seasonal patterns: average daily returns by month')
    plt.xticks(x, ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                   'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(data_dir / 'plots' / 'monthly_patterns.png')
    print(f"\n✅ chart saved to {data_dir / 'plots' / 'monthly_patterns.png'}")
    plt.close()

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