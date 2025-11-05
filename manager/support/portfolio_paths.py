from pathlib import Path

def which_portfolio(bhig_portfolio: bool = True) -> str:
    return ('BHIG' if bhig_portfolio else 'mock') + '_portfolio'

def DATA_FOLDER(bhig_portfolio: bool = True):
    return Path(__file__).resolve().parents[2] / 'data' / which_portfolio(bhig_portfolio)

transaction_data = lambda data_folder: data_folder / 'transactions.csv'
current_portfolio = lambda data_folder: data_folder / ''
current_portfolio_json = lambda data_folder: data_folder / ''
portfolio_json_file = lambda data_folder: data_folder / 'portfolio.json'
portfolio_file = lambda data_folder: data_folder / 'portfolio.csv'
returns_file = lambda data_folder: data_folder / 'returns.csv'