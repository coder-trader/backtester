import pandas as pd
from typing import Dict, Optional
from .base import StrategyBase


class RSIStrategy(StrategyBase):
    def __init__(
        self,
        initial_capital: float = 10000.0,
        oversold_threshold: float = 80.0,
        overbought_threshold: float = 20.0,
        take_profit_pct: float = 0.7,
        stop_loss_pct: float = 0.3,
    ):
        super().__init__(initial_capital)
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
        self.take_profit_pct = take_profit_pct / 100.0  # Convert to decimal
        self.stop_loss_pct = stop_loss_pct / 100.0  # Convert to decimal

    def on_tick(self, data: pd.Series, indicators: Dict[str, float]) -> Optional[str]:
        """
        RSI Strategy Logic with Take Profit and Stop Loss:
        - Buy (go long) when RSI > 80 (overbought reversal)
        - Sell (go short) when RSI < 20 (oversold reversal)
        - Take profit at 2% gain
        - Stop loss at 1% loss
        """
        rsi = indicators.get("rsi", 50.0)
        current_price = data["close"]

        # Check for take profit or stop loss if we have a position
        if self.position != 0:
            pnl_pct = self._calculate_pnl_percentage(current_price)

            # Take profit condition
            if pnl_pct >= self.take_profit_pct:
                return "close"

            # Stop loss condition
            elif pnl_pct <= -self.stop_loss_pct:
                return "close"

        # Entry signals (only if no position)
        if self.position == 0:
            # Buy signal when RSI is overbought (expecting reversal down, but strategy buys high)
            if rsi > self.overbought_threshold:
                return "buy"

            # Sell signal when RSI is oversold (expecting reversal up, but strategy shorts low)
            elif rsi < self.oversold_threshold:
                return "sell"

        return None

    def _calculate_pnl_percentage(self, current_price: float) -> float:
        """Calculate P&L as percentage of entry price"""
        if self.position == 0 or self.entry_price == 0:
            return 0.0

        if self.position == 1:  # Long position
            return (current_price - self.entry_price) / self.entry_price
        else:  # Short position (position == -1)
            return (self.entry_price - current_price) / self.entry_price
