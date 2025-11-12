# backtester/manual_backtest.py
# =============== 11/11 WEEK ASSIGNMENT ======================
# ===============   BACKTESTING   ====================

# Goal: Manually test a simple trading strategy on real data
# Focus: Understand how buy/sell signals translate to actual trades and profits
# Future: This teaches the foundation for automated backtesting systems

# ==========================================================
# CONCEPTUAL SECTION
# ----------------------------------------------------------


# ==========================================================
# TODO LEARN: walkthrough of Backtesting Step-by-Step (basic)
# ==========================================================
# Let's pretend we're testing our strategy on AAPL in early 2020
# We'll walk through EXACTLY what happens day by day
# 
# STRATEGY:
# Simple Momentum Strategy for ONE stock (AAPL)
# --------------------------------------------------
# BUY RULE:  When 20-day momentum > 5% (strong uptrend)
# SELL RULE: When 20-day momentum < -3% (downtrend) OR hold for 10 days
# Starting capital: $10,000
# Position size: Buy $1,000 worth each time
#
# STARTING POSITION (Jan 2, 2020):
# • Cash: $10,000
# • Shares owned: 0
# • AAPL price: $75.00
#
# ──────────────────────────────────────────────────────────
# DAY 1 (Jan 2, 2020): Calculate momentum
# ──────────────────────────────────────────────────────────
# Price today: $75.00
# Price 20 days ago: $70.00
# Momentum = (75 - 70) / 70 = +7.1%
# Signal: BUY (momentum > 5%)
# 
# ACTION: Buy AAPL!
# • Shares to buy: $1,000 / $75 = 13.33 shares
# • Cost: 13.33 × $75 = $999.75
# • New cash: $10,000 - $999.75 = $9,000.25
# • New shares: 13.33
# • Portfolio value: $9,000.25 + (13.33 × $75) = $10,000
#
# 📝 Trade recorded: BUY 13.33 shares @ $75.00
#
# ──────────────────────────────────────────────────────────
# DAY 5 (Jan 6, 2020): Check momentum again
# ──────────────────────────────────────────────────────────
# Price today: $76.50
# Price 20 days ago: $71.00
# Momentum = (76.50 - 71) / 71 = +7.7%
# Signal: BUY (momentum > 5%)
#
# ACTION: Buy more AAPL!
# • Shares to buy: $1,000 / $76.50 = 13.07 shares
# • Cost: 13.07 × $76.50 = $999.86
# • New cash: $9,000.25 - $999.86 = $8,000.39
# • New shares: 13.33 + 13.07 = 26.40
# • Portfolio value: $8,000.39 + (26.40 × $76.50) = $10,019.99
#
# 💰 Current profit: $10,019.99 - $10,000 = +$19.99 (+0.2%)
#
# 📝 Trade recorded: BUY 13.07 shares @ $76.50
#
# ──────────────────────────────────────────────────────────
# DAY 15 (Jan 17, 2020): Momentum drops
# ──────────────────────────────────────────────────────────
# Price today: $79.00
# Price 20 days ago: $77.50
# Momentum = (79 - 77.50) / 77.50 = +1.9%
# Signal: HOLD (momentum between -3% and +5%)
#
# ACTION: Do nothing, wait
# • Cash: $8,000.39
# • Shares: 26.40
# • Portfolio value: $8,000.39 + (26.40 × $79) = $10,086.99
#
# 💰 Current profit: $10,086.99 - $10,000 = +$86.99 (+0.87%)

# ──────────────────────────────────────────────────────────
# DAY 30 (Feb 3, 2020): Momentum turns negative
# ──────────────────────────────────────────────────────────
# Price today: $77.00
# Price 20 days ago: $79.50
# Momentum = (77 - 79.50) / 79.50 = -3.1%
# Signal: SELL (momentum < -3%)
#
# ACTION: Sell all AAPL!
# • Shares to sell: 26.40
# • Sale value: 26.40 × $77 = $2,032.80
# • New cash: $8,000.39 + $2,032.80 = $10,033.19
# • New shares: 0
# • Portfolio value: $10,033.19
#
# 💰 Total profit: $10,033.19 - $10,000 = +$33.19 (+0.33%)
#
# 📝 Trade recorded: SELL 26.40 shares @ $77.00
#
# ──────────────────────────────────────────────────────────
# FINAL RESULTS (End of test period):
# ──────────────────────────────────────────────────────────
# Starting capital: $10,000
# Ending capital: $10,033.19
# Total return: +0.33%
# Number of trades: 3 (2 buys, 1 sell)
#
# Compare to BUY-AND-HOLD:
# • If we bought on day 1 and held:
#   Shares: $10,000 / $75 = 133.33
#   Final value: 133.33 × $77 = $10,266.41
#   Buy-and-hold return: +2.66%
#
# 😞 Our strategy LOST to buy-and-hold by 2.33%!
#
# KEY INSIGHTS:
# ✅ We protected capital by selling when momentum turned negative
# ❌ We missed out on gains by selling too early
# 💡 Maybe we need different thresholds? Or different signals?
# 💡 This is why we backtest - to learn what works.
# ==========================================================

# 💡💡💡💡💡💡💡💡💡
# THINK ABOUT IT:
# • What "slippage" and "transaction costs" mean
# • Why some strategies look good but lose money
# • Do certain signals work for all stocks or some? If not what stocks can be grouped? 

# ==========================================================



# ==========================================================
# CODE SECTION
# ----------------------------------------------------------

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# ==========================================================
# 0. Loaded cleaned data 
# ----------------------------------------------------------
data_dir = Path("data")
clean_data_path = data_dir / "clean_prices.csv"

if not clean_data_path.exists():
    print("❌ Run dataloader.py first to generate clean_prices.csv")
    exit(1)

df = pd.read_csv(clean_data_path)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["ticker", "date"])

print("📊 Loaded cleaned price data for manual backtesting...\n")


# ==========================================================
# TODO CODE: Manual Backtesting (Week 3) - 5 Tasks
# ----------------------------------------------------------
# Goal: Test if a simple trading strategy actually makes money
# Process: Calculate signals → Generate trades → Track profits

# STRATEGY YOU'LL TEST:
# Simple Momentum Strategy for ONE stock (AAPL)
# --------------------------------------------------
# BUY RULE:  When 20-day momentum > 5% (strong uptrend)
# SELL RULE: When 20-day momentum < -3% (downtrend) OR hold for 10 days
# Starting capital: $10,000
# Position size: Buy $1,000 worth each time

# WHY ?
# By doing this, you'll understand:
# • How signals become actual trades
# • How to track your cash and stock positions
# • How to calculate profit/loss


def task1_calculate_signals(df, ticker="AAPL"):
    """Task 1: Calculate momentum signal for one stock"""
    # TODO: filter df for just the ticker (e.g., AAPL)
    # TODO: calculate 20-day momentum using .pct_change(periods=20)
    # TODO: create column 'momentum_20' with the values
    # TODO: print first 30 rows to see how momentum changes over time
    # HINT: momentum = (price_today / price_20_days_ago) - 1
    pass

def task2_generate_signals(stock_df):
    """Task 2: Generate buy/sell signals based on momentum"""
    # TODO: create 'signal' column with values: 'BUY', 'SELL', or 'HOLD'
    # TODO: BUY signal when momentum_20 > 0.05 (5%)
    # TODO: SELL signal when momentum_20 < -0.03 (-3%)
    # TODO: otherwise HOLD (no action)
    # TODO: print dates where BUY or SELL signals appear
    # EXAMPLE: 2020-03-15: BUY (momentum = 8.2%)
    pass

def task3_simulate_trades(stock_df, starting_cash=10000, position_size=1000):
    """Task 3: Manually execute trades based on signals"""
    # TODO: start with variables: cash = 10000, shares_owned = 0, trades = []
    # TODO: loop through each row of the dataframe
    # TODO: when signal = 'BUY' and have enough cash:
    #       - calculate shares to buy: position_size / current_price
    #       - subtract cost from cash
    #       - add shares to shares_owned
    #       - record trade: {date, action='BUY', price, shares, cash_remaining}
    # TODO: when signal = 'SELL' and shares_owned > 0:
    #       - calculate sale value: shares_owned * current_price
    #       - add to cash
    #       - set shares_owned = 0
    #       - record trade: {date, action='SELL', price, shares, cash_after}
    # TODO: return list of all trades
    # NOTE: This simulates you actually placing orders!
    pass

def task4_calculate_returns(trades, stock_df, starting_cash=10000):
    """Task 4: Calculate profit/loss and compare to buy-and-hold"""
    # TODO: calculate final portfolio value:
    #       final_value = current_cash + (shares_owned * final_price)
    # TODO: calculate total return: (final_value - starting_cash) / starting_cash
    # TODO: calculate buy-and-hold return for comparison:
    #       buy_and_hold = buy stock on day 1, hold until end
    #       shares = starting_cash / first_price
    #       final_value = shares * final_price
    #       return = (final_value - starting_cash) / starting_cash
    # TODO: print comparison:
    #       Strategy return: +15.2%
    #       Buy-and-hold return: +23.4%
    #       Strategy won/lost by: -8.2%
    # TODO: print number of trades executed
    pass

def task5_visualize_trades(stock_df, trades):
    """Task 5: Plot stock price with buy/sell markers"""
    # TODO: create figure with price chart
    # TODO: plot stock price over time as line chart
    # TODO: add green markers (^) at BUY trade dates
    # TODO: add red markers (v) at SELL trade dates
    # TODO: add legend showing what markers mean
    # TODO: save to data/plots/manual_backtest.png
    # VISUAL IMPACT: You'll SEE where you bought and sold!
    pass

# ==========================================================
# Bonus Task (Optional): Test Multiple Thresholds
# ----------------------------------------------------------

def bonus_test_thresholds():
    """Test different momentum thresholds to find the best strategy"""
    # TODO: try different buy/sell thresholds:
    #       Example: buy_threshold in [0.03, 0.05, 0.07, 0.10]
    #                sell_threshold in [-0.02, -0.03, -0.05]
    # TODO: run backtest for each combination
    # TODO: record returns for each
    # TODO: print which threshold combination works best
    # INSIGHT: Small changes in thresholds = differences in returns

    
    # feel free to try other stocks besides AAPL too!
    pass

# ==========================================================
# Main Execution
# ----------------------------------------------------------
if __name__ == "__main__":
    print("🎯 Week 3: Manual Backtesting - Test Your Strategy By Hand")
    print("📚 Goal: See if a momentum strategy actually makes money")
    print("💡 You'll track every trade manually to understand the process\n")
    
    print("📝 Strategy to test:")
    print("   • Stock: AAPL")
    print("   • BUY when momentum > 5%")
    print("   • SELL when momentum < -3%")
    print("   • Starting capital: $10,000")
    print("   • Position size: $1,000 per trade\n")
    
    print("📝 Complete these 5 tasks:")
    print("   1. Calculate Momentum Signal")
    print("   2. Generate Buy/Sell Signals")
    print("   3. Simulate Trades (execute buys/sells)")
    print("   4. Calculate Returns (profit/loss)")
    print("   5. Visualize Trades (chart with markers)\n")

    # TODO: uncomment as you complete each task
    # stock_df = task1_calculate_signals(df, ticker="AAPL")
    # stock_df = task2_generate_signals(stock_df)
    # trades = task3_simulate_trades(stock_df, starting_cash=10000, position_size=1000)
    # task4_calculate_returns(trades, stock_df, starting_cash=10000)
    # task5_visualize_trades(stock_df, trades)
    # 
    # BONUS:
    # bonus_test_thresholds()

    print("✅ Template ready - time to manually test your first strategy!")
    print("💡 Remember: Most strategies DON'T beat buy-and-hold. That's normal!")
    print("   The goal is to LEARN how backtesting works, not get rich quick.\n")
