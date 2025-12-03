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
    # 1. Filter for just the one stock
    stock_df = df[df["ticker"] == ticker].copy()

    # Make sure it's sorted by date (oldest -> newest)
    stock_df = stock_df.sort_values("date")

    # 2. Calculate 20-day momentum using pct_change
    # HINT from comments: momentum = (price_today / price_20_days_ago) - 1
    # Using .pct_change(20) does exactly that for 'close'
    stock_df["momentum_20"] = stock_df["close"].pct_change(periods=20)

    # 3. Print first 30 rows to inspect
    print(f"\n📈 Task 1: 20-day momentum for {ticker}")
    print(stock_df.head(30)[["date", "ticker", "close", "momentum_20"]])

    return stock_df


def task2_generate_signals(stock_df):
    """Task 2: Generate buy/sell signals based on momentum"""
    stock_df = stock_df.copy()

    # Default to HOLD
    stock_df["signal"] = "HOLD"

    # BUY when momentum_20 > 5%
    stock_df.loc[stock_df["momentum_20"] > 0.05, "signal"] = "BUY"

    # SELL when momentum_20 < -3%
    stock_df.loc[stock_df["momentum_20"] < -0.03, "signal"] = "SELL"

    # Print where BUY or SELL happens
    print("\n🎯 Task 2: BUY/SELL signal dates")
    signal_rows = stock_df[stock_df["signal"].isin(["BUY", "SELL"])]
    for _, row in signal_rows.iterrows():
        date_str = row["date"].strftime("%Y-%m-%d")
        print(f"  {date_str}: {row['signal']} (momentum = {row['momentum_20']:.2%})")

    return stock_df


def task3_simulate_trades(stock_df, starting_cash=10000, position_size=1000):
    """Task 3: Manually execute trades based on signals"""
    stock_df = stock_df.copy()

    cash = starting_cash
    shares_owned = 0.0
    trades = []

    print(f"\n💸 Task 3: Simulating trades (start cash=${starting_cash:,.2f})")

    # Iterate through each day in order
    for _, row in stock_df.iterrows():
        price = row["close"]
        signal = row["signal"]
        date = row["date"]

        # BUY: spend up to position_size, but not more cash than we have
        if signal == "BUY" and cash > price:
            # integer number of shares
            shares_to_buy = position_size // price
            shares_to_buy = int(shares_to_buy)

            if shares_to_buy > 0:
                cost = shares_to_buy * price
                # cap cost by available cash
                if cost > cash:
                    shares_to_buy = int(cash // price)
                    cost = shares_to_buy * price

                if shares_to_buy > 0:
                    cash -= cost
                    shares_owned += shares_to_buy

                    trades.append({
                        "date": date,
                        "action": "BUY",
                        "price": price,
                        "shares": shares_to_buy,
                        "cash_after": cash,
                        "shares_after": shares_owned,
                    })

        # SELL: sell all shares
        elif signal == "SELL" and shares_owned > 0:
            shares_to_sell = shares_owned
            proceeds = shares_to_sell * price
            cash += proceeds
            shares_owned = 0.0

            trades.append({
                "date": date,
                "action": "SELL",
                "price": price,
                "shares": shares_to_sell,
                "cash_after": cash,
                "shares_after": shares_owned,
            })

    print(f"  ➜ Completed {len(trades)} trades")
    return trades


def task4_calculate_returns(trades, stock_df, starting_cash=10000):
    """Task 4: Calculate profit/loss and compare to buy-and-hold"""
    stock_df = stock_df.sort_values("date").copy()
    first_price = stock_df["close"].iloc[0]
    final_price = stock_df["close"].iloc[-1]

    # Reconstruct final cash and shares from trades
    cash = starting_cash
    shares_owned = 0.0

    for tr in trades:
        if tr["action"] == "BUY":
            cost = tr["shares"] * tr["price"]
            cash -= cost
            shares_owned += tr["shares"]
        elif tr["action"] == "SELL":
            proceeds = tr["shares"] * tr["price"]
            cash += proceeds
            shares_owned -= tr["shares"]

    final_value = cash + shares_owned * final_price
    strategy_return = (final_value - starting_cash) / starting_cash

    # Buy-and-hold benchmark
    bh_shares = starting_cash / first_price
    bh_final_value = bh_shares * final_price
    bh_return = (bh_final_value - starting_cash) / starting_cash

    diff = strategy_return - bh_return

    print("\n📊 Task 4: Return comparison")
    print(f"   Strategy final value: ${final_value:,.2f}")
    print(f"   Strategy return:      {strategy_return:.2%}")
    print(f"   Buy & hold final:     ${bh_final_value:,.2f}")
    print(f"   Buy & hold return:    {bh_return:.2%}")
    print(f"   Strategy vs B&H:      {diff:+.2%}")
    print(f"   Number of trades:     {len(trades)}")

    # Optionally return metrics if you want to reuse later
    return {
        "final_value": final_value,
        "strategy_return": strategy_return,
        "buy_hold_return": bh_return,
        "excess_return": diff,
        "num_trades": len(trades),
    }

def task5_visualize_trades(stock_df, trades):
    """Task 5: Plot stock price with buy/sell markers"""
    stock_df = stock_df.sort_values("date").copy()

    plt.figure(figsize=(10, 5))

    # Plot price
    plt.plot(stock_df["date"], stock_df["close"], label="Price", linewidth=1.5)

    # Extract trade markers
    buy_dates = [tr["date"] for tr in trades if tr["action"] == "BUY"]
    buy_prices = [tr["price"] for tr in trades if tr["action"] == "BUY"]
    sell_dates = [tr["date"] for tr in trades if tr["action"] == "SELL"]
    sell_prices = [tr["price"] for tr in trades if tr["action"] == "SELL"]

    # Add buy markers (green ^) and sell markers (red v)
    if buy_dates:
        plt.scatter(buy_dates, buy_prices, marker="^", color="green", label="BUY", zorder=3)
    if sell_dates:
        plt.scatter(sell_dates, sell_prices, marker="v", color="red", label="SELL", zorder=3)

    plt.title("Manual Backtest: Price with Buy/Sell Trades")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()
    plt.grid(alpha=0.3)

    plots_dir = data_dir / "plots"
    plots_dir.mkdir(exist_ok=True)
    out_path = plots_dir / "manual_backtest.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    print(f"\n📉 Task 5: Plot saved to {out_path}")


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
    stock_df = task1_calculate_signals(df, ticker="AAPL")
    stock_df = task2_generate_signals(stock_df)
    trades = task3_simulate_trades(stock_df, starting_cash=10000, position_size=1000)
    task4_calculate_returns(trades, stock_df, starting_cash=10000)
    task5_visualize_trades(stock_df, trades)
    # BONUS:
    # bonus_test_thresholds()

    print("✅ Template ready - time to manually test your first strategy!")
    print("💡 Remember: Most strategies DON'T beat buy-and-hold. That's normal!")
    print("   The goal is to LEARN how backtesting works, not get rich quick.\n")