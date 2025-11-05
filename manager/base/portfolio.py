"""
portfolio.py

Defines the Portfolio class for managing a collection of asset positions.

The portfolio tracks cash, security holdings, and supports operations such as
transaction recording, valuation, and P&L analysis.

Author: Preetish Juneja, Adeethyia Shankar
Date: 2025-06-14
"""

from .transaction import Transaction
from .position import Position

class Portfolio:
    """
    Represents an investment portfolio containing positions in multiple assets.

    Tracks real-time cash, manages transaction history, and supports valuation,
    performance attribution, and portfolio-level analytics.

    Attributes
    ----------
    base_currency : str
        The default currency for all valuation and reporting (default is "USD").
    cash_position : float
        Cash held in the portfolio.
    positions : dict[str, Position]
        Dictionary of asset positions keyed by ticker.

    Methods
    -------
    to_dict() -> dict
        Returns a serializable dictionary of the portfolio state.
    add_transaction(transaction: Transaction)
        Adds a transaction to the appropriate position and updates cash.
    total_value(price_map: dict) -> float
        Calculates total portfolio value (positions + cash).
    total_unrealized_pnl(price_map: dict) -> float
        Computes unrealized profit/loss across all positions.
    total_realized_pnl() -> float
        Computes realized profit/loss using FIFO per position.
    get_cash() -> float
        Returns current cash balance.
    allocation_by(attribute: str, price_map: dict) -> dict[str, float]
        Computes portfolio allocation percentages by a given position attribute.
    summary()
        Prints a basic summary of portfolio holdings.
    """

    def __init__(self, cash: float = 0, base_currency: str = "USD", positions: dict[str, Position] = None):
        """
        Initialize a new portfolio.

        Parameters
        ----------
        cash : float, optional
            Initial cash position (default is 0).
        base_currency : str, optional
            Currency used for cash and position reporting (default is "USD").
        positions : dict[str, Position], optional
            Pre-existing positions dictionary (default is empty).
        """
        self.base_currency = base_currency
        self.cash_position = cash
        self.positions = positions if positions is not None else {}

    def to_dict(self):
        """
        Serialize the entire portfolio to a dictionary.

        Returns
        -------
        dict
            Dictionary containing cash, base currency, and all positions.
        """
        return {
            'base_currency': self.base_currency,
            'cash_position': self.cash_position,
            'positions': {ticker: position.to_dict() for ticker, position in self.positions.items()}
        }
    
    def get_tickers(self) -> list[str]:
        """
        Extract tickers from a Portfolio object.

        Parameters
        ----------
        pf : Portfolio
            The portfolio object containing assets.

        Returns
        -------
        list of str
            A list of tickers for all non-cash assets in the portfolio.
        """
        return list(self.positions.keys())

    def add_transaction(self, transaction: Transaction):
        """
        Add a new transaction and update positions and cash.

        If a new asset is introduced, creates a corresponding Position.

        Parameters
        ----------
        transaction : Transaction
            A buy or sell transaction to be processed.
        """
        if transaction.ticker not in self.positions:
            self.positions[transaction.ticker] = Position(
                ticker=transaction.ticker,
                asset_name=transaction.asset_name,
                asset_class=transaction.asset_class,
                exchange=transaction.exchange,
                currency=transaction.currency,
                sector=transaction.sector
            )
        self.positions[transaction.ticker].add_transaction(transaction)
        self.cash_position -= transaction.total_cost()

    def total_value(self, price_map: dict) -> float:
        """
        Compute total market value of the portfolio including cash.

        Parameters
        ----------
        price_map : dict[str, float]
            Dictionary mapping tickers to current market prices.

        Returns
        -------
        float
            Combined value of all positions and available cash.
        """
        return sum(
            pos.current_value(price_map.get(ticker, 0))
            for ticker, pos in self.positions.items()
        ) + self.cash_position

    def total_unrealized_pnl(self, price_map: dict) -> float:
        """
        Compute total unrealized profit/loss across all holdings.

        Parameters
        ----------
        price_map : dict[str, float]
            Dictionary mapping tickers to current market prices.

        Returns
        -------
        float
            Aggregated unrealized P&L.
        """
        return sum(
            pos.unrealized_pnl(price_map.get(ticker, 0))
            for ticker, pos in self.positions.items()
        )

    def total_realized_pnl(self) -> float:
        """
        Compute total realized profit/loss across all positions.

        Returns
        -------
        float
            Aggregated realized P&L (based on FIFO logic).
        """
        return sum(
            pos.realized_pnl()
            for _, pos in self.positions.items()
        )

    def get_cash(self) -> float:
        """
        Get current cash balance in the portfolio.

        Returns
        -------
        float
            Amount of uninvested cash.
        """
        return self.cash_position

    def allocation_by(self, attribute: str, price_map: dict) -> dict[str, float]:
        """
        Compute allocation breakdown by a position attribute (e.g., sector, asset_class).

        Parameters
        ----------
        attribute : str
            Name of the Position attribute to group by.
        price_map : dict[str, float]
            Dictionary mapping tickers to current market prices.

        Returns
        -------
        dict[str, float]
            Allocation percentages by group (normalized to 1.0).
        """
        allocation = {}
        total_val = self.total_value(price_map)
        if total_val == 0:
            return {}

        for ticker, pos in self.positions.items():
            attr_value = getattr(pos, attribute, "Unknown")
            val = pos.current_value(price_map.get(ticker, 0))
            allocation[attr_value] = allocation.get(attr_value, 0) + val

        for k in allocation:
            allocation[k] /= total_val
        return allocation
    
    def __repr__(self):
        portfolio_str = ''
        portfolio_str += f"Portfolio Summary ({self.base_currency})"
        portfolio_str += '\n'
        for pos in self.positions.values():
            portfolio_str += pos.__repr__()
            portfolio_str += '\n'
        portfolio_str += f"Total Cash: {self.cash_position:.2f} {self.base_currency}"
        return portfolio_str

    def summary(self):
        """
        Print a simple text summary of all current positions.
        """
        print(self)