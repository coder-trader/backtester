import pandas as pd
import numpy as np
import talib
from typing import Dict, Optional
from dataclasses import dataclass
from strategy.base import StrategyBase


@dataclass
class BacktestResults:
    initial_capital: float
    final_value: float
    total_return_pct: float
    max_drawdown_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    avg_win: float
    avg_loss: float
    equity_curve: pd.DataFrame
    trades: pd.DataFrame


class Backtester:
    def __init__(self, strategy: StrategyBase):
        self.strategy = strategy
        self.data: Optional[pd.DataFrame] = None
        self.results: Optional[BacktestResults] = None

    def load_data(self, csv_path: str) -> pd.DataFrame:
        """Load OHLCV data from CSV file"""
        try:
            df = pd.read_csv(csv_path)

            # Ensure required columns exist
            required_cols = ["open", "high", "low", "close", "volume"]
            if not all(col in df.columns.str.lower() for col in required_cols):
                raise ValueError(f"CSV must contain columns: {required_cols}")

            # Standardize column names
            df.columns = df.columns.str.lower()

            # Convert timestamp if exists
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df.set_index("timestamp", inplace=True)
            elif "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)

            self.data = df
            return df

        except Exception as e:
            raise ValueError(f"Error loading CSV data: {str(e)}")

    def calculate_indicators_at_index(self, current_idx: int) -> Dict[str, float]:
        """Calculate technical indicators for current candle"""
        indicators = {}

        # Need at least 14 periods for RSI
        start_idx = max(0, current_idx - 50)
        hist_data = self.data.iloc[start_idx : current_idx + 1]

        if len(hist_data) >= 14:
            # Calculate RSI
            rsi_values = talib.RSI(hist_data["close"].values, timeperiod=14)
            indicators["rsi"] = rsi_values[-1] if not np.isnan(rsi_values[-1]) else 50.0
        else:
            indicators["rsi"] = 50.0  # Default neutral RSI

        # Add more indicators as needed
        if len(hist_data) >= 20:
            # Simple Moving Average
            sma_values = talib.SMA(hist_data["close"].values, timeperiod=20)
            current_close = self.data.iloc[current_idx]["close"]
            indicators["sma_20"] = (
                sma_values[-1] if not np.isnan(sma_values[-1]) else current_close
            )

        return indicators

    def run(self, csv_path: str) -> BacktestResults:
        """Run the backtest"""
        # Load data
        df = self.load_data(csv_path)

        if df is None or len(df) == 0:
            raise ValueError("No data loaded")

        print(f"Running backtest with {len(df)} candles...")

        # Initialize results tracking
        equity_curve = []

        # Iterate through each candle
        for idx, (timestamp, row) in enumerate(df.iterrows()):
            # Calculate indicators (pass the current index for historical data lookup)
            indicators = self.calculate_indicators_at_index(idx)

            # Get strategy signal
            signal = self.strategy.on_tick(row, indicators)

            # Execute trade if signal exists
            if signal:
                self.strategy.execute_trade(signal, row["close"], str(timestamp))

            # Update current price for portfolio calculation
            self.strategy.current_price = row["close"]

            # Track equity curve
            portfolio_value = self.strategy.get_portfolio_value()
            equity_curve.append(
                {
                    "timestamp": timestamp,
                    "portfolio_value": portfolio_value,
                    "price": row["close"],
                }
            )

        # Calculate performance metrics
        results = self._calculate_performance(equity_curve)
        self.results = results

        return results

    def _calculate_performance(self, equity_curve: list) -> BacktestResults:
        """Calculate backtest performance metrics"""
        df_equity = pd.DataFrame(equity_curve)

        initial_capital = self.strategy.initial_capital
        final_value = df_equity["portfolio_value"].iloc[-1]

        total_return = (final_value - initial_capital) / initial_capital * 100

        # Calculate drawdown
        df_equity["peak"] = df_equity["portfolio_value"].expanding().max()
        df_equity["drawdown"] = (
            (df_equity["portfolio_value"] - df_equity["peak"]) / df_equity["peak"] * 100
        )
        max_drawdown = df_equity["drawdown"].min()

        # Trade statistics
        trades_df = pd.DataFrame(self.strategy.trades)

        if len(trades_df) > 0:
            profitable_trades = trades_df[trades_df["pnl"] > 0]
            losing_trades = trades_df[trades_df["pnl"] < 0]

            win_rate = (
                len(profitable_trades) / len(trades_df[trades_df["pnl"] != 0]) * 100
                if len(trades_df[trades_df["pnl"] != 0]) > 0
                else 0
            )
            avg_win = (
                profitable_trades["pnl"].mean() if len(profitable_trades) > 0 else 0
            )
            avg_loss = losing_trades["pnl"].mean() if len(losing_trades) > 0 else 0
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0

        return BacktestResults(
            initial_capital=initial_capital,
            final_value=final_value,
            total_return_pct=total_return,
            max_drawdown_pct=max_drawdown,
            total_trades=len(trades_df),
            winning_trades=len(profitable_trades) if len(trades_df) > 0 else 0,
            losing_trades=len(losing_trades) if len(trades_df) > 0 else 0,
            win_rate_pct=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            equity_curve=df_equity,
            trades=trades_df,
        )

    def print_results(self):
        """Print formatted backtest results"""
        if not self.results:
            print("No results available. Run backtest first.")
            return

        r = self.results
        print("=" * 50)
        print("BACKTEST RESULTS")
        print("=" * 50)
        print(f"Initial Capital: ${r.initial_capital:,.2f}")
        print(f"Final Value: ${r.final_value:,.2f}")
        print(f"Total Return: {r.total_return_pct:.2f}%")
        print(f"Max Drawdown: {r.max_drawdown_pct:.2f}%")
        print(f"Total Trades: {r.total_trades}")
        print(f"Winning Trades: {r.winning_trades}")
        print(f"Losing Trades: {r.losing_trades}")
        print(f"Win Rate: {r.win_rate_pct:.2f}%")
        print(f"Average Win: ${r.avg_win:.2f}")
        print(f"Average Loss: ${r.avg_loss:.2f}")
        print("=" * 50)
