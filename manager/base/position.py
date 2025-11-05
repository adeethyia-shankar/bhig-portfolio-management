"""
position.py

Defines the Position class used for tracking security holdings within a portfolio.

Each Position object maintains metadata, cumulative cost and quantity, and a FIFO-based
record of historical transactions to enable cost basis, realized P&L, and valuation metrics.

Author: Preetish Juneja, Adeethyia Shankar
Date: 2025-06-14
"""

from collections import deque
from .transaction import Transaction

class Position:
    """
    Represents a held position in a financial asset.

    A Position aggregates all transactions related to a given security (buy/sell)
    and tracks metrics such as average cost, realized/unrealized P&L, and valuation.

    Attributes
    ----------
    ticker : str
        Unique identifier for the asset (e.g., "AAPL").
    asset_name : str
        Full name of the security (e.g., "Apple Inc.").
    asset_class : str
        Category of the asset (e.g., "Equity", "Bond", "ETF").
    exchange : str
        Exchange where the asset is listed.
    currency : str
        Quoted currency for the asset (default is "USD").
    sector : str, optional
        Industry sector associated with the asset.
    cost : float
        Running total of invested capital including fees.
    quantity : float
        Net units held (positive = long, negative = short).
    transactions : deque of Transaction
        Historical transaction records used for P&L and cost basis tracking.

    Methods
    -------
    to_dict() -> dict
        Returns a dictionary serialization of the position.
    add_transaction(transaction: Transaction)
        Appends a transaction and updates cost and quantity.
    current_quantity() -> float
        Returns the net number of units held.
    average_cost() -> float
        Returns the average cost per unit (weighted by quantity).
    realized_pnl() -> float
        Calculates realized P&L using FIFO methodology.
    current_value(price: float) -> float
        Returns current market value of the position.
    unrealized_pnl(price: float) -> float
        Computes unrealized P&L based on current price vs. average cost.
    __repr__() -> str
        Returns a string summary of the position.
    """

    def __init__(self, ticker: str, asset_name: str, asset_class: str, exchange: str,
                 sector: str, currency: str = "USD", cost: float = 0, quantity: float = 0):
        self.ticker = ticker
        self.asset_name = asset_name
        self.asset_class = asset_class
        self.exchange = exchange
        self.currency = currency
        self.sector = sector
        self.cost = cost
        self.quantity = quantity
        self.transactions = deque()

    def to_dict(self):
        """
        Serialize the position to a dictionary.

        Returns
        -------
        dict
            Dictionary containing position metadata and transaction list.
        """
        return {
            'ticker': self.ticker,
            'asset_name': self.asset_name,
            'asset_class': self.asset_class,
            'exchange': self.exchange,
            'currency': self.currency,
            'sector': self.sector,
            'cost': self.cost,
            'quantity': self.quantity,
            'transactions': [t.to_dict() for t in self.transactions]
        }

    def add_transaction(self, transaction: Transaction):
        """
        Add a transaction and update position cost and quantity.

        Parameters
        ----------
        transaction : Transaction
            The transaction to be added. Must match the position's ticker.
        """
        assert transaction.ticker == self.ticker
        self.cost += transaction.total_cost()
        self.quantity += transaction.quantity
        self.transactions.append(transaction)

    def current_quantity(self) -> float:
        """
        Get the current quantity held.

        Returns
        -------
        float
            Net number of units held.
        """
        return self.quantity

    def average_cost(self) -> float:
        """
        Calculate the average cost per unit held.

        Returns
        -------
        float
            Weighted average cost basis (0 if quantity is zero).
        """
        return self.cost / self.quantity if self.quantity != 0 else 0

    def realized_pnl(self) -> float:
        """
        Calculate realized P&L using FIFO method.

        Returns
        -------
        float
            Total realized profit or loss from closed positions.
        """
        realized = 0.0
        fifo_stack = []

        for t in self.transactions:
            if t.quantity > 0:
                fifo_stack.append([t.quantity, (t.price + t.fees) / t.quantity])  # [quantity, cost_per_unit]
            elif t.quantity < 0:
                qty_to_sell = t.quantity
                sell_price = t.price
                while qty_to_sell > 0 and fifo_stack:
                    lot_qty, lot_price = fifo_stack[0]
                    if qty_to_sell < lot_qty:
                        realized += qty_to_sell * (sell_price - lot_price)
                        fifo_stack[0][0] -= qty_to_sell
                        qty_to_sell = 0
                    else:
                        realized += lot_qty * (sell_price - lot_price)
                        qty_to_sell -= lot_qty
                        fifo_stack.pop(0)
        return realized

    def current_value(self, price: float) -> float:
        """
        Calculate the current market value of the position.

        Parameters
        ----------
        price : float
            Current market price of the asset.

        Returns
        -------
        float
            Market value (quantity × price).
        """
        return self.current_quantity() * price

    def unrealized_pnl(self, price: float) -> float:
        """
        Calculate unrealized profit or loss.

        Parameters
        ----------
        price : float
            Current market price of the asset.

        Returns
        -------
        float
            Difference between market value and cost basis.
        """
        return (price - self.average_cost()) * self.current_quantity()

    def __repr__(self) -> str:
        """
        Return a string representation of the position.

        Returns
        -------
        str
            Summary including ticker, quantity, and average cost.
        """
        return f"{self.ticker}: {self.current_quantity()} units @ avg cost {self.average_cost():.2f} {self.currency}"
