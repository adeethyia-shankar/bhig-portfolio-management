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
    # did some extra: added more detailed analysis (latest 10 days buying and selling)
    
    print("\n" + "="*60)
    print(f"task 1: calculating momentum signal for {ticker}")
    print("="*60)
    
    # step 1: filter for just one stock (AAPL)
    # why? we want to test our strategy on one stock first before expanding
    stock_df = df[df['ticker'] == ticker].copy()
    print(f"\n✅ filtered to {ticker}: {len(stock_df)} trading days")
    
    # step 2: calculate 20-day momentum
    # formula: momentum = (price_today / price_20_days_ago) - 1
    # example: if price was $100 twenty days ago and is $110 today:
    #          momentum = (110 / 100) - 1 = 0.10 or +10%
    stock_df['momentum_20'] = stock_df['close'].pct_change(periods=20)
    
    print(f"\n📊 momentum calculation:")
    print(f"   • lookback period: 20 days")
    print(f"   • first 20 days will be NaN (not enough history)")
    print(f"   • positive momentum = price trending UP")
    print(f"   • negative momentum = price trending DOWN")
    
    # step 3: show first 30 rows with valid momentum (no NaN)
    valid_data = stock_df.dropna(subset=['momentum_20'])
    
    print(f"\n📈 first 30 days with valid momentum:")
    print(valid_data[['date', 'close', 'momentum_20']].head(30).to_string())
    
    # step 4: show 10 latest days with BUY signals (momentum > 5%)
    buy_signals = valid_data[valid_data['momentum_20'] > 0.05]
    print(f"\n🟢 10 LATEST days with BUY signal (momentum > 5%):")
    print(buy_signals[['date', 'close', 'momentum_20']].tail(10).to_string())
    
    # step 5: show 10 latest days with SELL signals (momentum < -3%)
    sell_signals = valid_data[valid_data['momentum_20'] < -0.03]
    print(f"\n🔴 10 LATEST days with SELL signal (momentum < -3%):")
    print(sell_signals[['date', 'close', 'momentum_20']].tail(10).to_string())
    
    return stock_df

def task2_generate_signals(stock_df):
    """Task 2: Generate buy/sell signals based on momentum"""
    # TODO: create 'signal' column with values: 'BUY', 'SELL', or 'HOLD'
    # TODO: BUY signal when momentum_20 > 0.05 (5%)
    # TODO: SELL signal when momentum_20 < -0.03 (-3%)
    # TODO: otherwise HOLD (no action)
    # TODO: print dates where BUY or SELL signals appear
    # EXAMPLE: 2020-03-15: BUY (momentum = 8.2%)
    # did latest 30 day with signals, 10 latest buy/sell/hold signals, summary counts
    
    print("\n" + "="*60)
    print("task 2: generate buy/sell signals")
    print("="*60)
    
    # step 1: create signal column based on momentum thresholds
    # BUY: momentum > 5%
    # SELL: momentum < -3%
    # HOLD: everything else
    def get_signal(momentum):
        if pd.isna(momentum):
            return 'HOLD'
        elif momentum > 0.05:
            return 'BUY'
        elif momentum < -0.03:
            return 'SELL'
        else:
            return 'HOLD'
    
    stock_df['signal'] = stock_df['momentum_20'].apply(get_signal)
    
    print(f"\n✅ signals generated based on rules:")
    print(f"   • BUY when momentum > 5%")
    print(f"   • SELL when momentum < -3%")
    print(f"   • HOLD otherwise")
    
    # step 2: show latest 30 days with signals
    print(f"\n📅 latest 30 days with signals:")
    print(stock_df[['date', 'close', 'momentum_20', 'signal']].tail(30).to_string())
    
    # step 3: show 10 latest BUY signals
    buy_days = stock_df[stock_df['signal'] == 'BUY']
    print(f"\n🟢 10 LATEST BUY signals:")
    print(buy_days[['date', 'close', 'momentum_20', 'signal']].tail(10).to_string())
    
    # step 4a: show 10 latest SELL signals
    sell_days = stock_df[stock_df['signal'] == 'SELL']
    print(f"\n🔴 10 LATEST SELL signals (not all will execute):")
    print(sell_days[['date', 'close', 'momentum_20', 'signal']].tail(10).to_string())
    
    # step 4b: note - actual SELL trades shown later after simulation
    print(f"\n   💡 Note: SELL signals only execute when you own shares!")
    print(f"   💡 Actual SELL trades will be shown after task 3 simulation.")
    
    # step 5: show 10 latest HOLD signals
    hold_days = stock_df[stock_df['signal'] == 'HOLD']
    print(f"\n🟡 10 LATEST HOLD signals:")
    print(hold_days[['date', 'close', 'momentum_20', 'signal']].tail(10).to_string())
    
    # summary
    buy_count = len(buy_days)
    sell_count = len(sell_days)
    hold_count = len(hold_days)
    print(f"\n📊 signal summary:")
    print(f"   • total BUY signals: {buy_count}")
    print(f"   • total SELL signals: {sell_count}")
    print(f"   • total HOLD signals: {hold_count}")
    
    return stock_df

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
    
    print("\n" + "="*60)
    print("task 3: simulate trades")
    print("="*60)
    
    # step 1: initialize trading variables
    cash = starting_cash
    shares_owned = 0
    trades = []
    
    print(f"\n💰 starting portfolio:")
    print(f"   • cash: ${cash:,.2f}")
    print(f"   • shares: {shares_owned}")
    print(f"   • position size per trade: ${position_size:,.2f}")
    
    # step 2: loop through each day and execute trades
    for idx, row in stock_df.iterrows():
        date = row['date']
        price = row['close']
        signal = row['signal']
        
        # BUY logic
        if signal == 'BUY' and cash >= position_size:
            # calculate how many shares we can buy
            shares_to_buy = position_size / price
            cost = shares_to_buy * price
            
            # execute the trade
            cash -= cost
            shares_owned += shares_to_buy
            
            # record the trade
            trades.append({
                'date': date,
                'action': 'BUY',
                'price': price,
                'shares': shares_to_buy,
                'cash': cash,
                'shares_owned': shares_owned,
                'portfolio_value': cash + (shares_owned * price)
            })
        
        # SELL logic
        elif signal == 'SELL' and shares_owned > 0:
            # calculate sale value
            sale_value = shares_owned * price
            
            # execute the trade
            cash += sale_value
            shares_sold = shares_owned
            shares_owned = 0
            
            # record the trade
            trades.append({
                'date': date,
                'action': 'SELL',
                'price': price,
                'shares': shares_sold,
                'cash': cash,
                'shares_owned': shares_owned,
                'portfolio_value': cash
            })
    
    # step 3: convert trades to dataframe for easier viewing
    trades_df = pd.DataFrame(trades)
    
    print(f"\n📋 executed {len(trades_df)} trades total")
    print(f"   • BUY trades: {len(trades_df[trades_df['action'] == 'BUY'])}")
    print(f"   • SELL trades: {len(trades_df[trades_df['action'] == 'SELL'])}")
    
    # step 4: show first 30 trades
    print(f"\n📊 first 30 trades:")
    print(trades_df.head(30).to_string())
    
    # step 4b: show 10 latest ACTUAL SELL trades (where stock was sold)
    sell_trades = trades_df[trades_df['action'] == 'SELL']
    if len(sell_trades) > 0:
        print(f"\n🔴 10 LATEST ACTUAL SELL TRADES (stock sold):")
        print(sell_trades[['date', 'action', 'price', 'shares', 'cash', 'portfolio_value']].tail(10).to_string())
    else:
        print(f"\n🔴 No SELL trades executed (never owned shares to sell)")
    
    # step 5: calculate final portfolio value
    final_price = stock_df.iloc[0]['close']  # most recent price
    final_portfolio_value = cash + (shares_owned * final_price)
    
    print(f"\n💼 final portfolio:")
    print(f"   • cash: ${cash:,.2f}")
    print(f"   • shares owned: {shares_owned:.2f}")
    print(f"   • final stock price: ${final_price:.2f}")
    print(f"   • total portfolio value: ${final_portfolio_value:,.2f}")
    
    return trades_df, cash, shares_owned

def task4_calculate_returns(trades_df, stock_df, cash, shares_owned, starting_cash=10000):
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
    
    print("\n" + "="*60)
    print("task 4: calculate returns")
    print("="*60)
    
    # step 1: calculate strategy returns
    final_price = stock_df.iloc[0]['close']  # most recent price
    final_portfolio_value = cash + (shares_owned * final_price)
    strategy_return = (final_portfolio_value - starting_cash) / starting_cash
    
    print(f"\n📈 strategy performance:")
    print(f"   • starting capital: ${starting_cash:,.2f}")
    print(f"   • final portfolio value: ${final_portfolio_value:,.2f}")
    print(f"   • total return: {strategy_return*100:+.2f}%")
    print(f"   • profit/loss: ${final_portfolio_value - starting_cash:+,.2f}")
    
    # step 2: calculate buy-and-hold returns
    first_valid_price = stock_df[stock_df['signal'].notna()].iloc[-1]['close']
    shares_if_bought_and_held = starting_cash / first_valid_price
    buy_hold_final_value = shares_if_bought_and_held * final_price
    buy_hold_return = (buy_hold_final_value - starting_cash) / starting_cash
    
    print(f"\n🔵 buy-and-hold performance (for comparison):")
    print(f"   • if bought on first day: {shares_if_bought_and_held:.2f} shares @ ${first_valid_price:.2f}")
    print(f"   • final value: ${buy_hold_final_value:,.2f}")
    print(f"   • total return: {buy_hold_return*100:+.2f}%")
    print(f"   • profit/loss: ${buy_hold_final_value - starting_cash:+,.2f}")
    
    # step 3: compare strategy vs buy-and-hold
    difference = strategy_return - buy_hold_return
    
    print(f"\n⚖️  comparison:")
    if difference > 0:
        print(f"   ✅ strategy BEAT buy-and-hold by {difference*100:+.2f}%")
    else:
        print(f"   ❌ strategy LOST to buy-and-hold by {difference*100:.2f}%")
    
    # step 4: trade statistics
    print(f"\n📊 trade statistics:")
    print(f"   • total trades executed: {len(trades_df)}")
    print(f"   • BUY trades: {len(trades_df[trades_df['action'] == 'BUY'])}")
    print(f"   • SELL trades: {len(trades_df[trades_df['action'] == 'SELL'])}")
    
    return strategy_return, buy_hold_return

def task5_visualize_trades(stock_df, trades_df):
    """Task 5: Plot stock price with buy/sell markers"""
    # TODO: create figure with price chart
    # TODO: plot stock price over time as line chart
    # TODO: add green markers (^) at BUY trade dates
    # TODO: add red markers (v) at SELL trade dates
    # TODO: add legend showing what markers mean
    # TODO: save to data/plots/manual_backtest.png
    # VISUAL IMPACT: You'll SEE where you bought and sold!
    
    print("\n" + "="*60)
    print("task 5: visualize trades")
    print("="*60)
    
    # create figure
    plt.figure(figsize=(14, 7))
    
    # plot stock price
    plt.plot(stock_df['date'], stock_df['close'], 
             label='AAPL Price', color='black', linewidth=1.5, alpha=0.7)
    
    # add BUY markers
    buy_trades = trades_df[trades_df['action'] == 'BUY']
    plt.scatter(buy_trades['date'], buy_trades['price'],
                marker='^', color='green', s=150, label='BUY', zorder=5, edgecolors='darkgreen', linewidth=1.5)
    
    # add SELL markers
    sell_trades = trades_df[trades_df['action'] == 'SELL']
    plt.scatter(sell_trades['date'], sell_trades['price'], 
                marker='v', color='red', s=150, label='SELL', zorder=5, edgecolors='darkred', linewidth=1.5)
    
    # formatting
    plt.title('AAPL Trading Strategy: Price & Trade Execution', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price ($)', fontsize=12)
    plt.legend(loc='best', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # save plot
    import os
    output_path = 'data/plots/manual_backtest.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n📊 chart saved to: {output_path}")
    plt.close()
    
    print(f"✅ visualization complete!")
    print(f"   • {len(buy_trades)} BUY trades marked in green")
    print(f"   • {len(sell_trades)} SELL trades marked in red")
    
    # portfolio value over time
    print(f"\n📊 creating portfolio value chart...")
    
    # track portfolio value day by day
    daily_portfolio = []
    cash_track = 10000
    shares_track = 0
    trade_idx = 0
    
    for idx, row in stock_df.iterrows():
        date = row['date']
        price = row['close']
        
        # check if there's a trade on this day
        if trade_idx < len(trades_df) and trades_df.iloc[trade_idx]['date'] == date:
            trade = trades_df.iloc[trade_idx]
            cash_track = trade['cash']
            shares_track = trade['shares_owned']
            trade_idx += 1
        
        # calculate portfolio value for this day
        stock_value = shares_track * price
        total_value = cash_track + stock_value
        
        daily_portfolio.append({
            'date': date,
            'cash': cash_track,
            'stock_value': stock_value,
            'total_value': total_value
        })
    
    daily_df = pd.DataFrame(daily_portfolio)
    
    # create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # subplot 1: portfolio value line chart
    ax1.plot(daily_df['date'], daily_df['total_value'], 
             label='Total Portfolio Value', color='purple', linewidth=2)
    ax1.axhline(y=10000, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Starting Capital')
    ax1.set_title('Portfolio Value Over Time', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Portfolio Value ($)', fontsize=12)
    ax1.legend(loc='best', fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # subplot 2: stacked bar chart (cash vs stock holdings)
    ax2.bar(daily_df['date'], daily_df['cash'], label='Cash', color='green', alpha=0.7)
    ax2.bar(daily_df['date'], daily_df['stock_value'], bottom=daily_df['cash'], 
            label='Stock Holdings', color='blue', alpha=0.7)
    ax2.set_title('Portfolio Composition: Cash vs Stock Holdings', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Value ($)', fontsize=12)
    ax2.legend(loc='best', fontsize=11)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # save plot
    output_path2 = 'data/plots/portfolio_value.png'
    plt.savefig(output_path2, dpi=150, bbox_inches='tight')
    print(f"📊 portfolio value chart saved to: {output_path2}")
    plt.close()

# ==========================================================
# Bonus Task (Optional): Test Multiple Thresholds
# ----------------------------------------------------------

def bonus_test_thresholds():
    """Test contrarian strategy: buy dips, sell rallies"""
    print("\n" + "="*60)
    print("BONUS: test contrarian strategy thresholds")
    print("="*60)
    print("💡 Strategy: BUY when momentum drops (buy the dip)")
    print("            SELL when momentum rises (take profits)")
    
    # get AAPL data
    stock_df = df[df['ticker'] == 'AAPL'].copy()
    stock_df['momentum_20'] = stock_df['close'].pct_change(periods=20)
    
    # test different threshold combinations
    buy_thresholds = [-0.15, -0.10, -0.05]  # buy when momentum THIS LOW (negative)
    sell_thresholds = [0.05, 0.07, 0.10]    # sell when momentum THIS HIGH (positive)
    
    results = []

    for buy_thresh in buy_thresholds:
        for sell_thresh in sell_thresholds:
            # generate signals
            test_df = stock_df.copy()
            test_df['signal'] = 'HOLD'
            test_df.loc[test_df['momentum_20'] <= buy_thresh, 'signal'] = 'BUY'
            test_df.loc[test_df['momentum_20'] >= sell_thresh, 'signal'] = 'SELL'
            
            # simulate trades
            cash = 10000
            shares_owned = 0
            trades = []
            
            for idx, row in test_df.iterrows():
                price = row['close']
                signal = row['signal']
                
                if signal == 'BUY' and cash >= 1000:
                    shares_to_buy = 1000 / price
                    cash -= 1000
                    shares_owned += shares_to_buy
                    trades.append('BUY')
                    
                elif signal == 'SELL' and shares_owned > 0:
                    cash += shares_owned * price
                    shares_owned = 0
                    trades.append('SELL')
            
            # calculate final value
            final_price = test_df.iloc[-1]['close']
            final_value = cash + (shares_owned * final_price)
            total_return = ((final_value - 10000) / 10000) * 100
            
            results.append({
                'buy_threshold': buy_thresh,
                'sell_threshold': sell_thresh,
                'final_value': final_value,
                'return_pct': total_return,
                'num_trades': len(trades)
            })
    
    # show results
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('return_pct', ascending=False)
    
    print(f"\n📊 tested {len(results_df)} threshold combinations:")
    print(results_df.to_string(index=False))
    
    # get S&P 500 benchmark (simple buy and hold)
    import yfinance as yf
    sp_data = yf.download('^GSPC', start='2024-11-03', end='2025-11-03', progress=False)
    sp_start = float(sp_data['Close'].iloc[0])
    sp_end = float(sp_data['Close'].iloc[-1])
    sp_return = ((sp_end - sp_start) / sp_start) * 100
    sp_final_value = 10000 * (1 + sp_return/100)
    
    print(f"\n🔵 S&P 500 buy-and-hold (benchmark):")
    print(f"   • start price: ${sp_start:.2f}")
    print(f"   • end price: ${sp_end:.2f}")
    print(f"   • final value: ${sp_final_value:,.2f}")
    print(f"   • return: {sp_return:.2f}%")
    print(f"   💡 Just bought at start, held, sold at end - NO trading!")
    
    best = results_df.iloc[0]
    print(f"\n🏆 BEST contrarian strategy:")
    print(f"   • BUY when momentum <= {best['buy_threshold']:.2%}")
    print(f"   • SELL when momentum >= {best['sell_threshold']:.2%}")
    print(f"   • final value: ${best['final_value']:,.2f}")
    print(f"   • return: {best['return_pct']:.2f}%")
    print(f"   • trades executed: {int(best['num_trades'])}")
    
    # compare best strategy to S&P
    if best['return_pct'] > sp_return:
        diff = best['return_pct'] - sp_return
        print(f"\n   ✅ BEAT S&P 500 by {diff:.2f}%!")
    else:
        diff = sp_return - best['return_pct']
        print(f"\n   ❌ S&P 500 beat this by {diff:.2f}%")
        print(f"\n   💡 Lesson: Trading is HARD. Buy-and-hold of just S&P usually wins, and even wins over a lot of hedge funds :/")
    
    # visualize best strategy vs S&P 500
    print(f"\n📊 creating comparison chart...")
    
    # run best strategy to get daily portfolio values
    test_df = stock_df.copy()
    test_df['signal'] = 'HOLD'
    test_df.loc[test_df['momentum_20'] <= best['buy_threshold'], 'signal'] = 'BUY'
    test_df.loc[test_df['momentum_20'] >= best['sell_threshold'], 'signal'] = 'SELL'
    
    # simulate to track daily portfolio value
    cash = 10000
    shares_owned = 0
    strategy_values = []
    
    for idx, row in test_df.iterrows():
        date = row['date']
        price = row['close']
        signal = row['signal']
        
        if signal == 'BUY' and cash >= 1000:
            shares_to_buy = 1000 / price
            cash -= 1000
            shares_owned += shares_to_buy
        elif signal == 'SELL' and shares_owned > 0:
            cash += shares_owned * price
            shares_owned = 0
        
        portfolio_value = cash + (shares_owned * price)
        strategy_values.append({'date': date, 'value': portfolio_value})
    
    strategy_df = pd.DataFrame(strategy_values)
    
    # calculate S&P 500 daily portfolio values
    sp_shares = 10000 / sp_start
    sp_daily = sp_data.reset_index()
    sp_daily['portfolio_value'] = sp_shares * sp_daily['Close']
    sp_daily = sp_daily.rename(columns={'Date': 'date'})
    
    # create comparison plot
    plt.figure(figsize=(14, 7))
    
    plt.plot(strategy_df['date'], strategy_df['value'], 
             label=f'Best Strategy (BUY≤{best["buy_threshold"]:.1%}, SELL≥{best["sell_threshold"]:.1%})', 
             color='green', linewidth=2)
    plt.plot(sp_daily['date'], sp_daily['portfolio_value'], 
             label='S&P 500 Buy-and-Hold', 
             color='blue', linewidth=2, alpha=0.7)
    plt.axhline(y=10000, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Starting Capital')
    
    plt.title(f'Best Strategy vs S&P 500: Portfolio Value Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Portfolio Value ($)', fontsize=12)
    plt.legend(loc='best', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # save plot
    buy_str = f"{abs(best['buy_threshold']):.2f}".replace('.', '_')
    sell_str = f"{abs(best['sell_threshold']):.2f}".replace('.', '_')
    output_path3 = f'data/plots/buy_{buy_str}_sell_{sell_str}_vs_sp500.png'
    plt.savefig(output_path3, dpi=150, bbox_inches='tight')
    print(f"📊 comparison chart saved to: {output_path3}")
    plt.close()

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
    trades_df, cash, shares_owned = task3_simulate_trades(stock_df, starting_cash=10000, position_size=1000)
    task4_calculate_returns(trades_df, stock_df, cash, shares_owned, starting_cash=10000)
    task5_visualize_trades(stock_df, trades_df)
    
    # BONUS:
    bonus_test_thresholds()

    print("\n✅ Task 1 complete - momentum signals calculated!")
    print("💡 Remember: Most strategies DON'T beat buy-and-hold. That's normal!")
    print("   The goal is to LEARN how backtesting works, not get rich quick.\n")
