"""
transactions.py

Module for representing and handling financial transactions within a portfolio.

Defines the Transaction data structure, which tracks metadata and financial impact of individual security trades.

Author: Preetish Juneja, Adeethyia Shankar
Date: 2025-06-14
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    """
    Represents a single transaction of a financial asset within a portfolio.

    Each transaction includes metadata such as ticker symbol, asset class,
    quantity traded, execution price, and other optional contextual data
    (e.g., sector, exchange, currency).

    Attributes
    ----------
    ticker : str
        The security identifier, ideally in the format "TICKER:EXCHANGE" (e.g., "AAPL:NASDAQ").
    asset_name : str
        Full name of the asset (e.g., "Apple Inc.").
    asset_class : str
        Type of asset (e.g., "Equity", "Bond", "ETF", "Crypto").
    quantity : float
        Number of units transacted. Positive for buys, negative for sells.
    price : float
        Execution price per unit of the asset.
    date : datetime
        Date and time of the transaction.
    currency : str, optional
        Quoted currency of the transaction (default is "USD").
    exchange : str, optional
        Name of the exchange where the asset is traded (e.g., "NASDAQ").
    sector : str, optional
        Industry sector associated with the asset (e.g., "Healthcare").
    fees : float, optional
        Total transaction fees (always positive). Default is 0.0.
    notes : str, optional
        Arbitrary string for user comments or tagging.

    Methods
    -------
    to_dict() -> dict
        Converts the transaction object into a serializable dictionary.
    total_cost() -> float
        Computes the full dollar impact of the transaction, including fees.
    """

    ticker: str
    asset_name: str
    asset_class: str
    quantity: float
    price: float
    date: datetime
    exchange: str
    sector: str
    currency: str = "USD"
    fees: float = 0.0
    notes: Optional[str] = None

    def to_dict(self):
        """
        Convert the transaction to a dictionary for serialization or export.

        Returns
        -------
        dict
            Dictionary representation of the transaction with stringified date.
        """
        return {
            "ticker": self.ticker,
            "asset_name": self.asset_name,
            "asset_class": self.asset_class,
            "quantity": self.quantity,
            "price": self.price,
            "date": str(self.date),
            "currency": self.currency,
            "exchange": self.exchange,
            "sector": self.sector,
            "fees": self.fees,
            "notes": self.notes
        }

    def total_cost(self) -> float:
        """
        Compute the total cost (or proceeds) of the transaction.

        This includes the product of quantity and price, adjusted for any fees.

        Returns
        -------
        float
            Total dollar impact of the transaction.
        """
        return (self.quantity * self.price) + self.fees
