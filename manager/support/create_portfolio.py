# use this file to create/update portfolio as necessary

import json
import csv
from datetime import datetime
import pandas as pd
from ..base.portfolio import *
from .get_current_prices import *
from .portfolio_paths import *

## TODO: add support for dividends and stock splits for equities
def load_transactions_from_csv(file_path: str, ignore_accounted: bool = True) -> list[Transaction]:
    transactions = []
    transactions_df = pd.read_csv(file_path)
    for row in transactions_df.itertuples():
        if row.asset_name == 'Cash':
            continue
        elif row.accounted and ignore_accounted:
            continue
        elif not row.accounted and ignore_accounted:
            transactions_df.at[row.Index, 'accounted'] = True
        sign = 1 if row.transaction_type == 'BUY' else -1
        transactions.append(Transaction(
            ticker=row.ticker,
            asset_name=row.asset_name,
            asset_class=row.asset_class,
            quantity=float(sign*row.quantity),
            price=float(row.price),
            date=pd.to_datetime(row.date),
            currency=getattr(row, 'currency', 'USD'),
            exchange=getattr(row, 'exchange', None),
            sector=getattr(row, 'sector', None),
            fees=float(getattr(row, 'fees', 0.0)),
            notes=getattr(row, 'notes', None)
        ))

    if ignore_accounted:
        transactions_df.to_csv(file_path, index=False)
        
    return transactions

## use this as a backup if no json for portfolio object is available
def load_portfolio_from_csv(file_path: str) -> Portfolio:
    """
    file_path must be a csv file in the portfolio's format
    """
    cash = 0
    positions = {}
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['asset_name'] == 'Cash':
                cash = float(row["current price"])
                continue
            positions[row["ticker"]] = Position(
                ticker=row["ticker"],
                asset_name=row["asset_name"],
                asset_class=row["asset_class"],
                exchange=row["exchange"],
                currency=row.get("currency", "USD"),
                sector=row.get("sector", "NA"),
                cost=float(row["cost"])*float(row.get("quantity")),
                quantity=float(row.get("quantity")),
            )
    return Portfolio(cash = cash, positions = positions)

## use this as the preferred function using a json file
def load_portfolio(file_path: str) -> Portfolio:
    """
    file_path must be a json file for a portfolio object
    """
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Create empty portfolio
    portfolio = Portfolio(base_currency=data["base_currency"])
    portfolio.cash_position = float(data.get("cash_position", 0.0))

    for _, pos_data in data["positions"].items():
        # Create Position
        position = Position(
            ticker=pos_data["ticker"],
            asset_name=pos_data["asset_name"],
            asset_class=pos_data["asset_class"],
            exchange=pos_data["exchange"],
            currency=pos_data["currency"],
            sector=pos_data["sector"],
            cost=float(pos_data["cost"]),
            quantity=float(pos_data["quantity"])
        )

        # Add Transactions
        for txn_data in pos_data.get("transactions", []):
            txn = Transaction(
                ticker=txn_data["ticker"],
                asset_name=txn_data["asset_name"],
                asset_class=txn_data["asset_class"],
                quantity=float(txn_data["quantity"]),
                price=float(txn_data["price"]),
                date=pd.to_datetime(txn_data["date"]),
                currency=txn_data["currency"],
                exchange=txn_data["exchange"],
                sector=txn_data.get("sector"),
                fees=float(txn_data.get("fees", 0.0)),
                notes=txn_data.get("notes")
            )
            position.transactions.append(txn)
        
        portfolio.positions[pos_data["ticker"]] = position

    return portfolio

## to be used to calculate the day's portfolio value and then add it to an existing returns file
def add_returns(portfolio: Portfolio, price_map: dict[str, float], file_path: str, date: datetime = datetime.today()):
    fieldnames = ["date", "portfolio_value", "total_cash", "total_realized_pnl", "total_unrealized_pnl"]

    with open(file_path, mode="a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow({
            "date": date.strftime('%Y-%m-%d'),
            "portfolio_value": portfolio.total_value(price_map),
            "total_cash": portfolio.get_cash(),
            "total_realized_pnl": portfolio.total_realized_pnl(),
            "total_unrealized_pnl": portfolio.total_unrealized_pnl(price_map)
        })

def calculate_returns(portfolio: Portfolio, start_date: str, end_date: str, file_path: str):
    price_data = get_prices(portfolio.get_tickers(), start_date, end_date)
    for date, price_map in price_data.items():
        add_returns(portfolio, price_map, file_path, date=date)

## TODO: add support for storing realized pnl of both open and closed positions
def export_portfolio_to_csv(portfolio: Portfolio, current_prices: dict, filename: str):
    fieldnames = ["ticker", "asset_name", "asset_class", "exchange", "cost", "current price", "quantity", "pnl", "currency", "sector"]

    with open(filename, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for _, position in portfolio.positions.items():
            if int(position.quantity):
                writer.writerow({
                    "ticker": position.ticker,
                    "asset_name": position.asset_name,
                    "asset_class": position.asset_class,
                    "exchange": position.exchange,
                    "cost": round(position.average_cost(), 4),
                    "current price": current_prices.get(position.ticker, 0),
                    "quantity": round(position.current_quantity(), 4),
                    "pnl": position.unrealized_pnl(current_prices.get(position.ticker, 0)),
                    "currency": position.currency,
                    "sector": position.sector
                })
        
        writer.writerow({"asset_name": "Cash", "current price": portfolio.get_cash()})
