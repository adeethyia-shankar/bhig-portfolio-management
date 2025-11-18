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

"""


import pandas as pd
import numpy as np
from dataloader import load_clean_data
# Import the manual backtest functions you already wrote! 
# (please change these function names change depending on your implementation)
from manual_backtest import (
    task1_calculate_signals,
    task2_generate_signals, 
    task3_simulate_trades,
    task4_calculate_returns
)

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
        # TODO: load clean price data using load_clean_data()
        # TODO: store as self.data
        # TODO: store ticker, starting_cash, position_size as self.ticker, self.starting_cash, self.position_size
        # TODO: initialize self.params = {} (will be set later with set_params)
        
        print(f"🔧 Backtester initialized for {ticker}")
        print(f"   • starting cash: ${starting_cash:,.2f}")
        print(f"   • position size per BUY: ${position_size:,.2f}")
        print(f"   • SELL behavior: sells ALL shares at once")
        
        pass  # REMOVE this once you add your code
    
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
        # TODO: store params as instance variable
        # TODO: validate that required keys exist (signal_type, buy_threshold, sell_threshold)
        # TODO: print confirmation of parameters set
        
        print(f"\n📋 Parameters set:")
        print(f"   • signal: {params.get('signal_type', 'NOT SET')}")
        print(f"   • buy threshold: {params.get('buy_threshold', 'NOT SET')}")
        print(f"   • sell threshold: {params.get('sell_threshold', 'NOT SET')}")
        
        pass  # REMOVE this once you add your code
    
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
        print("\n" + "="*60)
        print(f"RUNNING BACKTEST: {self.ticker}")
        print("="*60)
        
        # TODO: Step 1 - Calculate signals
        #       Use your task1 function to calculate momentum/signals
        print("\n🎯 Step 1: Calculate signals")
        # YOUR CODE HERE, under a function (not just driver code)
        
        # TODO: Step 2 - Generate BUY/SELL/HOLD labels 
        #       Use your task2 function to create trading signals
        print("\n🎯 Step 2: Generate BUY/SELL/HOLD signals")
        # YOUR CODE HERE
        
        # TODO: Step 3 - Simulate trades
        #       Use your task3 function to execute trades
        print("\n🎯 Step 3: Simulate trades")
        # YOUR CODE HERE
        
        # TODO: Step 4 - Calculate returns
        #       Use your task4 function to compute performance
        print("\n🎯 Step 4: Calculate returns")
        # YOUR CODE HERE
        
        print("\n✅ Backtest complete!")
        
        # TODO: Build and return results dictionary
        #       Include: final_value, return_pct, num_trades, trades_df, etc.
        return {}  # REPLACE with actual results dictionary
    


    # NOTE: This is all just a guide. Keep in mind the goal is just so the backtester
    # can run the full backtest given parameters, not inputted like one stock at a time
    # and position size at a time. all should work in this format: 

    # backtester = Backtester(ticker='any ticker', starting_cash= x, position_size=y)
    # backtester.set_params(params={'buy_threshold': 0.05, 'sell_threshold': -0.03})
    
    # Run backtest and get results
    results = backtester.backtest()
    print(results)
    # backtester.set_params(params={'buy_threshold': 0.05, 'sell_threshold': -0.03})


# ==========================================================
# Example Usage (Driver Code, UNDERSTAND THIS)
# ----------------------------------------------------------

if __name__ == "__main__":
    print("🎯 Week 4: Backtester Class")
    print("📚 Goal: Build a reusable backtesting tool\n")
    
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
    print(results)
    
    print("\n💡 Next steps:")
    print("   1. Complete the TODOs in each method")
    print("   2. Test with different parameters")
    print("   3. Add support for more signal types (z-score, volatility, etc.)")
    print("   4. Add visualization methods")
    print("   5. Compare multiple strategies side-by-side")
    
    # ==========================================================
    # TODO: Test your backtester with different parameters to see if it works!
    # ==========================================================
    print("\n" + "="*60)
    print("🎓 YOUR TURN: Test on a different stock!")
    print("="*60)
    
    # TODO: Create your own backtester for NVDA (NVIDIA)
    # Example:
    #   nvda_backtester = Backtester(ticker='NVDA', starting_cash=20000, position_size=2000)
    #   nvda_backtester.set_params(params={'buy_threshold': 0.03, 'sell_threshold': -0.02})
    #   nvda_results = nvda_backtester.backtest()
    #   print(nvda_results)
    
    # TODO: Try MSFT with different thresholds 
    # Example:
    #   msft_backtester = Backtester(ticker='MSFT', starting_cash=15000, position_size=1500)
    #   msft_backtester.set_params(params={'buy_threshold': 0.07, 'sell_threshold': -0.05})
    #   msft_results = msft_backtester.backtest()
    #   print(msft_results)
    
    # TODO: Compare which stock/strategy performed best. 
    # The code above uncommented should 
    # all work if you implemented the Backtester class correctly so far! 
    
    print("\n💡 Tips for experimentation:")
    print("   • Aggressive: buy_threshold=0.03, sell_threshold=-0.02 (more trades)")
    print("   • Conservative: buy_threshold=0.07, sell_threshold=-0.05 (fewer trades)")
    print("   • Try different position sizes: $500, $2000, $5000 per trade")
    print("   • Available stocks: AAPL, MSFT, META, BLK, PYPL, SHOP, NVDA")
