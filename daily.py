## TODO: write the script that will be run daily for portfolio updates (i.e. using something like 
## create_portfolio.py from manager/support/) and analysis (i.e. using some version of files from
## manager/analysis/))

"""
daily.py

Defines the daily_update function for daily portfolio updates

Supports both the BHIG and mock portfolios

Author: Adeethyia Shankar
Date: 2025-10-07
"""

from manager.support.create_portfolio import *

def daily_update(bhig_portfolio: bool = True):
    data_folder = DATA_FOLDER(bhig_portfolio)
    print(f'Data folder: {data_folder}')

    pf = load_portfolio_from_csv(portfolio_file(data_folder))
    print(f'Portfolio: {pf}')
    
    transactions = load_transactions_from_csv(transaction_data(data_folder))
    for t in transactions:
        pf.add_transaction(t)
    
    current_prices = get_current_prices(pf.get_tickers())
    print(f'Current prices: {current_prices}')

    # Print valuations
    print("\nValuation")
    print(f"Total Value: ${pf.total_value(current_prices):.2f}")
    print(f"Unrealized P&L: ${pf.total_unrealized_pnl(current_prices):.2f}")

    # Create csv for portfolio
    export_portfolio_to_csv(pf, current_prices, portfolio_file(data_folder))

    # Create json for portfolio
    with open(portfolio_json_file(data_folder), 'w') as fp:
        json.dump(pf.to_dict(), fp)

    # Add portfolio's value to the returns file
    add_returns(pf, current_prices, returns_file(data_folder))

daily_update(True)