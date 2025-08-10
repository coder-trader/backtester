from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Optional


class StrategyBase(ABC):
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0  # 0 = no position, 1 = long, -1 = short
        self.entry_price = 0.0
        self.trades = []
        self.current_price = 0.0

    @abstractmethod
    def on_tick(self, data: pd.Series, indicators: Dict[str, float]) -> Optional[str]:
        """
        Called on each new candle/tick.

        Args:
            data: Current OHLCV data as pandas Series
            indicators: Dictionary of calculated indicators

        Returns:
            Action to take: 'buy', 'sell', 'close' or None
        """
        pass

    def get_portfolio_value(self) -> float:
        """Calculate current portfolio value"""
        if self.position == 0:
            return self.capital
        elif self.position == 1:  # Long position
            return self.capital + (self.current_price - self.entry_price)
        else:  # Short position
            return self.capital + (self.entry_price - self.current_price)

    def execute_trade(self, action: str, price: float, timestamp: str):
        """Execute a trade action"""
        if action == "buy" and self.position <= 0:
            if self.position == -1:  # Close short position first
                pnl = self.entry_price - price
                self.capital += pnl
                self.trades.append(
                    {
                        "timestamp": timestamp,
                        "action": "close_short",
                        "price": price,
                        "pnl": pnl,
                    }
                )

            # Open long position
            self.position = 1
            self.entry_price = price
            self.trades.append(
                {"timestamp": timestamp, "action": "buy", "price": price, "pnl": 0}
            )

        elif action == "sell" and self.position >= 0:
            if self.position == 1:  # Close long position first
                pnl = price - self.entry_price
                self.capital += pnl
                self.trades.append(
                    {
                        "timestamp": timestamp,
                        "action": "close_long",
                        "price": price,
                        "pnl": pnl,
                    }
                )

            # Open short position
            self.position = -1
            self.entry_price = price
            self.trades.append(
                {"timestamp": timestamp, "action": "sell", "price": price, "pnl": 0}
            )

        elif action == "close":
            if self.position == 1:  # Close long
                pnl = price - self.entry_price
                self.capital += pnl
                self.trades.append(
                    {
                        "timestamp": timestamp,
                        "action": "close_long",
                        "price": price,
                        "pnl": pnl,
                    }
                )
            elif self.position == -1:  # Close short
                pnl = self.entry_price - price
                self.capital += pnl
                self.trades.append(
                    {
                        "timestamp": timestamp,
                        "action": "close_short",
                        "price": price,
                        "pnl": pnl,
                    }
                )

            self.position = 0
            self.entry_price = 0.0

        self.current_price = price
