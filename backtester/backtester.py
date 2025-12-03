# backtester/backtester.py
"""
Week 4: Build a Backtester Class 

MAKE SURE TO READ THIS IN IT'S ENTIRETY from lines 1-60 BEFORE CODING

================================= 
Goal: Create a reusable backtesting tool that can test ANY stock with ANY parameters
      using the buy/sell strategy from manual_backtest.py.

💡 RECOMMENDATION: You CAN use any functions from manual_backtest.py
   The goal is to wrap your manual backtest work into a REUSABLE tool.

📝 Strategy Parameters (Current Implementation):
   - ticker: Which stock to trade (AAPL, MSFT, META, etc.)
   - starting_cash: Initial capital (e.g., $10,000)
   - position_size: How much $ to spend on EACH BUY (e.g., $1000 per trade)
   - buy_threshold: Momentum % to trigger BUY signal (e.g., 0.05 = buy when momentum > 5%)
   - sell_threshold: Momentum % to trigger SELL signal (e.g., -0.03 = sell when momentum < -3%)

📝 Trading Rules (Current Implementation):
   BUY: Purchases $position_size worth of stock each time
        Example: If position_size=$1000 and price=$50, buys 20 shares
   
   SELL: Sells ALL shares owned (not partial sells)
         Example: If you own 60 shares, sells all 60 shares at once

📝 Future Enhancements (NOT YET IMPLEMENTED):
   - buy_signal: Different signal types ('momentum', 'z-score', 'volatility', etc.)
   - sell_signal: Different signal types (currently momentum only)
   - buy_size: Variable position sizing (currently fixed at position_size)
   - sell_size: Partial sells (currently sells all shares)

CURRENT USAGE EXAMPLE (Current Implementation):
    # Create backtester for Microsoft with $50k capital, $2k per trade
    backtester = Backtester(ticker='MSFT', starting_cash=50000, position_size=2000)
    
    # Set strategy thresholds
    backtester.set_params(params={'buy_threshold': 0.05, 'sell_threshold': -0.03})
    
    # Run backtest and get results
    results = backtester.backtest()
    print(results)

FUTURE usage example (Future Enhancements - NOT YET IMPLEMENTED):
    # Create backtester for Microsoft with $50k capital, $2k per trade
    backtester = Backtester(ticker='MSFT', starting_cash=50000, position_size=2000)
    
    # Set advanced strategy parameters (FUTURE)
    backtester.set_params(params={
        'buy_signal': 'z-score',        # Use z-score instead of momentum
        'sell_signal': 'volatility',    # Use volatility for sell signals
        'buy_threshold': 0.05,
        'sell_threshold': -0.03,
        'buy_size': 1500,               # Variable buy amounts
        'sell_size': 0.5                # Sell 50% of shares (partial sell)
    })
    
    # Run backtest and get results
    results = backtester.backtest()
    print(results)

 * * * * * * * ** * * CONCEPTUAL QUESTION * * * * * * ** * * * * * *

    backtester = Backtester(ticker='abcd', starting_cash=x, position_size=pos)
    backtester.set_params(params={'buy_threshold': bt, 'sell_threshold': st})

    For this backtester to do what is done in manual_backtest.py's implementation, what
    are the values of x, pos, bt, st? 

    ANSWER:
    Looking at manual_backtest.py's main execution:
    - x = 10000 (starting_cash=10000)
    - pos = 1000 (position_size=1000)
    - bt = 0.05 (buy when momentum > 5%)
    - st = -0.03 (sell when momentum < -3%)

"""


import pandas as pd
import numpy as np
from pathlib import Path

# Import functions from manual_backtest.py
# Note: Adjust these imports based on your actual function names
from manual_backtest import (
    task1_calculate_signals,
    task2_generate_signals, 
    task3_simulate_trades,
    task4_calculate_returns
)

# ==========================================================
# Helper function to load clean data
# ----------------------------------------------------------

def load_clean_data():
    """
    Load the cleaned price data from data/clean_prices.csv
    
    Returns:
        pd.DataFrame: Cleaned price data with columns [date, ticker, close, volume]
    """
    data_dir = Path("data")
    clean_data_path = data_dir / "clean_prices.csv"
    
    if not clean_data_path.exists():
        raise FileNotFoundError(
            f"❌ {clean_data_path} not found. Run fetch_yfinance.py first to generate clean data."
        )
    
    df = pd.read_csv(clean_data_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ticker", "date"])
    
    return df


# ==========================================================
# Backtester Class
# ----------------------------------------------------------

class Backtester:
    """
    A reusable backtesting engine that can test different trading strategies.
    
    Architecture:
        1. __init__: Load data and set defaults
        2. set_params: Configure strategy parameters
        3. backtest: Run the full backtest with given signal
        4. _calculate_signals: Generate trading signals (internal)
        5. _simulate_trades: Execute trades (internal)
        6. _calculate_returns: Compute performance metrics (internal)
    """
    
    def __init__(self, ticker='AAPL', starting_cash=10000, position_size=1000):
        """
        Initialize the backtester with default settings
        for example default stock here is AAPL
        
        Args:
            ticker (str): Stock symbol to backtest (AAPL, MSFT, META, etc.)
            starting_cash (float): Starting capital ($10,000 default)
            position_size (float): $ amount to BUY each time (e.g., $1000 per BUY trade)
                                   NOTE: SELL always sells ALL shares (no position_size for sells)
        """
        # Load clean price data
        self.data = load_clean_data()  # make sure your dataloader returns full DataFrame
        
        # Store settings
        self.ticker = ticker
        self.starting_cash = starting_cash
        self.position_size = position_size
        self.params = {}  # will be set later with set_params
        
        # Validate ticker exists in data
        available_tickers = self.data['ticker'].unique()
        if ticker not in available_tickers:
            raise ValueError(
                f"❌ Ticker '{ticker}' not found in data. "
                f"Available tickers: {', '.join(available_tickers)}"
            )
        
        print(f"🔧 Backtester initialized for {ticker}")
        print(f"   • starting cash: ${starting_cash:,.2f}")
        print(f"   • position size per BUY: ${position_size:,.2f}")
        print(f"   • SELL behavior: sells ALL shares at once")
    
    def set_params(self, params):
        """
        Set strategy parameters.
        
        Args:
            params (dict): Strategy parameters, e.g.:
                {
                    'signal_type': 'momentum',
                    'lookback': 20,
                    'buy_threshold': 0.05,
                    'sell_threshold': -0.03
                }
        """
        # Store parameters
        self.params = params
        
        # Validate required keys exist
        required = ['signal_type', 'lookback', 'buy_threshold', 'sell_threshold']
        for key in required:
            if key not in params:
                raise ValueError(f"Missing required parameter: {key}")
        
        # Validate parameter values
        if params['lookback'] <= 0:
            raise ValueError("lookback must be positive")
        if params['buy_threshold'] <= params['sell_threshold']:
            raise ValueError("buy_threshold must be greater than sell_threshold")
        
        # Print confirmation
        print(f"\n📋 Parameters set:")
        print(f"   • signal: {params.get('signal_type', 'NOT SET')}")
        print(f"   • lookback: {params.get('lookback', 'NOT SET')}")
        print(f"   • buy threshold: {params.get('buy_threshold', 'NOT SET')}")
        print(f"   • sell threshold: {params.get('sell_threshold', 'NOT SET')}")
    
    def backtest(self, signal=None): 
        """
        Run the full backtest pipeline.
        
        💡 APPROACH: GIVEN THE PARAMETERS ABOVE, 
        Write code (could use functions from manual_backtest.py if you want) to:
           1. Calculate signals (e.g., momentum)
           2. Generate BUY/SELL/HOLD labels
           3. Simulate trades (execute buys/sells)
           4. Calculate returns (strategy vs buy-and-hold)
        
        Then return a results dictionary with key metrics.
        
        Args:
            signal (str): Signal type to use (e.g., 'momentum')
        
        Returns:
            dict: Backtest results including final_value, return_pct, num_trades, trades_df
        """
        # Validate that parameters have been set
        if not self.params:
            raise ValueError(
                "❌ Parameters not set. Call set_params() before running backtest."
            )
        
        print("\n" + "="*60)
        print(f"RUNNING BACKTEST: {self.ticker}")
        print("="*60)
        
        # Step 1 - Calculate signals
        print("\n🎯 Step 1: Calculate signals")
        stock_df = task1_calculate_signals(self.data, ticker=self.ticker)
        
        # Check if we have enough data after calculating signals
        if stock_df['momentum_20'].notna().sum() < 10:
            print(f"⚠️ Warning: Only {stock_df['momentum_20'].notna().sum()} valid momentum values.")
            print("   Consider using more historical data or a shorter lookback period.")
        
        # Step 2 - Generate BUY/SELL/HOLD labels with custom thresholds
        print("\n🎯 Step 2: Generate BUY/SELL/HOLD signals")
        
        # Override task2 signals with our custom thresholds from params
        buy_th = self.params['buy_threshold']
        sell_th = self.params['sell_threshold']
        
        # Initialize all as HOLD
        stock_df['signal'] = 'HOLD'
        
        # Apply BUY signal when momentum exceeds buy threshold
        stock_df.loc[stock_df['momentum_20'] > buy_th, 'signal'] = 'BUY'
        
        # Apply SELL signal when momentum falls below sell threshold
        stock_df.loc[stock_df['momentum_20'] < sell_th, 'signal'] = 'SELL'
        
        # Count and display signals
        signal_counts = stock_df['signal'].value_counts()
        print(f"   Signal distribution:")
        for sig, count in signal_counts.items():
            print(f"      {sig}: {count} days")
        
        # Step 3 - Simulate trades
        print("\n🎯 Step 3: Simulate trades")
        trades = task3_simulate_trades(
            stock_df,
            starting_cash=self.starting_cash,
            position_size=self.position_size
        )
        
        # Validate trades
        if len(trades) == 0:
            print("⚠️ Warning: No trades generated. Strategy may be too conservative.")
        
        # Step 4 - Calculate returns
        print("\n🎯 Step 4: Calculate returns")
        results = task4_calculate_returns(
            trades, 
            stock_df, 
            starting_cash=self.starting_cash
        )
        
        # Add additional useful information to results
        results['ticker'] = self.ticker
        results['trades_df'] = pd.DataFrame(trades) if trades else pd.DataFrame()
        results['params'] = self.params.copy()
        results['starting_cash'] = self.starting_cash
        results['position_size'] = self.position_size
        
        # Calculate additional metrics
        if len(trades) > 0:
            trades_df = pd.DataFrame(trades)
            buy_trades = trades_df[trades_df['action'] == 'BUY']
            sell_trades = trades_df[trades_df['action'] == 'SELL']
            
            results['num_buys'] = len(buy_trades)
            results['num_sells'] = len(sell_trades)
            
            # Average trade metrics
            if len(buy_trades) > 0:
                results['avg_buy_price'] = buy_trades['price'].mean()
            if len(sell_trades) > 0:
                results['avg_sell_price'] = sell_trades['price'].mean()
        else:
            results['num_buys'] = 0
            results['num_sells'] = 0
        
        print("\n✅ Backtest complete!")
        return results


# ==========================================================
# Example Usage (Driver Code, UNDERSTAND THIS)
# ----------------------------------------------------------

if __name__ == "__main__":
    print("🎯 Week 4: Backtester Class")
    print("📚 Goal: Build a reusable backtesting tool\n")
    
    # ==========================================================
    # Test 1: AAPL with default manual_backtest.py parameters
    # ==========================================================
    print("\n" + "="*60)
    print("TEST 1: AAPL (matching manual_backtest.py)")
    print("="*60)
    
    # Step 1: Create backtester instance
    print("Step 1: Initialize backtester")
    backtester = Backtester(ticker='AAPL', starting_cash=10000, position_size=1000)
    
    # Step 2: Set parameters
    print("\nStep 2: Set strategy parameters")
    params_dict = {
        'signal_type': 'momentum',
        'lookback': 20,
        'buy_threshold': 0.05,    # buy when momentum > 5%
        'sell_threshold': -0.03   # sell when momentum < -3%
    }
    backtester.set_params(params=params_dict)
    
    # Step 3: Run backtest
    print("\nStep 3: Run backtest")
    results = backtester.backtest(signal='momentum')
    
    # Step 4: Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Ticker: {results['ticker']}")
    print(f"Final Value: ${results['final_value']:,.2f}")
    print(f"Strategy Return: {results['strategy_return']:.2%}")
    print(f"Buy & Hold Return: {results['buy_hold_return']:.2%}")
    print(f"Excess Return: {results['excess_return']:+.2%}")
    print(f"Number of Trades: {results['num_trades']}")
    print(f"  - Buys: {results['num_buys']}")
    print(f"  - Sells: {results['num_sells']}")
    
    if results['num_buys'] > 0:
        print(f"Average Buy Price: ${results['avg_buy_price']:.2f}")
    if results['num_sells'] > 0:
        print(f"Average Sell Price: ${results['avg_sell_price']:.2f}")
    
    # ==========================================================
    # Test 2: MSFT with more conservative strategy
    # ==========================================================
    print("\n\n" + "="*60)
    print("TEST 2: MSFT (conservative strategy)")
    print("="*60)
    
    msft_bt = Backtester(ticker='MSFT', starting_cash=15000, position_size=1500)
    msft_bt.set_params({
        'signal_type': 'momentum', 
        'lookback': 20, 
        'buy_threshold': 0.07,    # Higher threshold = fewer buys
        'sell_threshold': -0.05   # Lower threshold = fewer sells
    })
    msft_results = msft_bt.backtest()
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Ticker: {msft_results['ticker']}")
    print(f"Final Value: ${msft_results['final_value']:,.2f}")
    print(f"Strategy Return: {msft_results['strategy_return']:.2%}")
    print(f"Buy & Hold Return: {msft_results['buy_hold_return']:.2%}")
    print(f"Excess Return: {msft_results['excess_return']:+.2%}")
    print(f"Number of Trades: {msft_results['num_trades']}")
    
    # ==========================================================
    # Test 3: META with aggressive strategy
    # ==========================================================
    print("\n\n" + "="*60)
    print("TEST 3: META (aggressive strategy)")
    print("="*60)
    
    meta_bt = Backtester(ticker='META', starting_cash=20000, position_size=2000)
    meta_bt.set_params({
        'signal_type': 'momentum', 
        'lookback': 20, 
        'buy_threshold': 0.03,    # Lower threshold = more buys
        'sell_threshold': -0.02   # Higher threshold = more sells
    })
    meta_results = meta_bt.backtest()
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Ticker: {meta_results['ticker']}")
    print(f"Final Value: ${meta_results['final_value']:,.2f}")
    print(f"Strategy Return: {meta_results['strategy_return']:.2%}")
    print(f"Buy & Hold Return: {meta_results['buy_hold_return']:.2%}")
    print(f"Excess Return: {meta_results['excess_return']:+.2%}")
    print(f"Number of Trades: {meta_results['num_trades']}")
    
    # ==========================================================
    # Summary comparison
    # ==========================================================
    print("\n\n" + "="*60)
    print("SUMMARY COMPARISON")
    print("="*60)
    
    comparison = pd.DataFrame([
        {
            'Ticker': results['ticker'],
            'Strategy': 'Default',
            'Final Value': results['final_value'],
            'Return': results['strategy_return'],
            'vs B&H': results['excess_return'],
            'Trades': results['num_trades']
        },
        {
            'Ticker': msft_results['ticker'],
            'Strategy': 'Conservative',
            'Final Value': msft_results['final_value'],
            'Return': msft_results['strategy_return'],
            'vs B&H': msft_results['excess_return'],
            'Trades': msft_results['num_trades']
        },
        {
            'Ticker': meta_results['ticker'],
            'Strategy': 'Aggressive',
            'Final Value': meta_results['final_value'],
            'Return': meta_results['strategy_return'],
            'vs B&H': meta_results['excess_return'],
            'Trades': meta_results['num_trades']
        }
    ])
    
    print(comparison.to_string(index=False))
    
    # ==========================================================
    # Tips for experimentation
    # ==========================================================
    print("\n\n💡 Tips for experimentation:")
    print("   • Aggressive: buy_threshold=0.03, sell_threshold=-0.02 (more trades)")
    print("   • Conservative: buy_threshold=0.07, sell_threshold=-0.05 (fewer trades)")
    print("   • Try different position sizes: $500, $2000, $5000 per trade")
    print("   • Available stocks: AAPL, MSFT, META, BLK, PYPL, SHOP")
    print("\n📊 Next steps:")
    print("   1. Test different thresholds to optimize returns")
    print("   2. Compare multiple stocks with same strategy")
    print("   3. Analyze which market conditions favor your strategy")
    print("   4. Consider transaction costs (not yet implemented)")