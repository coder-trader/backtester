import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

import ccxt
import pandas as pd


@dataclass
class CandleData:
    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float


class CandleDataCollector:
    def __init__(self, exchange_name: str = "binance"):
        """
        Initialize the candle data collector

        Args:
            exchange_name: Name of the exchange (e.g., 'binance', 'coinbase', 'kraken')
        """
        self.exchange_name = exchange_name.lower()
        self.exchange = self._init_exchange()

    def _init_exchange(self) -> ccxt.Exchange:
        """Initialize the CCXT exchange instance"""
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            exchange = exchange_class(
                {
                    "sandbox": False,  # Set to True for testnet/sandbox
                    "rateLimit": 1200,  # milliseconds
                    "enableRateLimit": True,
                }
            )
            return exchange
        except AttributeError:
            available_exchanges = ccxt.exchanges
            raise ValueError(
                f"Exchange '{self.exchange_name}' not supported. "
                f"Available exchanges: {', '.join(available_exchanges[:10])}..."
            )

    def get_available_symbols(self) -> List[str]:
        """Get list of available trading symbols for the exchange"""
        assert self.exchange.symbols is not None
        try:
            self.exchange.load_markets()
            return list(self.exchange.symbols)
        except Exception as e:
            print(f"Error loading markets: {e}")
            return []

    def get_available_timeframes(self) -> List[str]:
        """Get list of available timeframes for the exchange"""
        return list(self.exchange.timeframes.keys()) if self.exchange.timeframes else []

    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parse datetime string to datetime object"""
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y/%m/%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse datetime: {dt_str}")

    def collect_candles(
        self,
        symbol: str,
        timeframe: str = "1h",
        start_time: str = "2024-08-08",
        end_time: str = "2024-08-09",
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Collect candle data from the exchange

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d', etc.)
            start_time: Start time as string (e.g., '2023-01-01', '2023-01-01 12:00:00')
            end_time: End time as string (e.g., '2023-01-31', '2023-01-31 23:59:59')
            limit: Maximum number of candles per request (exchange dependent)

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            # Load markets to ensure symbol exists
            self.exchange.load_markets()

            assert self.exchange.symbols is not None

            if symbol not in self.exchange.symbols:
                available_symbols = list(self.exchange.symbols)[:10]
                raise ValueError(
                    f"Symbol '{symbol}' not available. "
                    f"Example symbols: {', '.join(available_symbols)}..."
                )

            if timeframe not in self.exchange.timeframes:
                available_timeframes = list(self.exchange.timeframes.keys())
                raise ValueError(
                    f"Timeframe '{timeframe}' not supported. "
                    f"Available: {', '.join(available_timeframes)}"
                )

            # Parse start and end times
            since = None
            until = None

            if start_time:
                start_dt = self._parse_datetime(start_time)
                since = int(start_dt.timestamp() * 1000)

            if end_time:
                end_dt = self._parse_datetime(end_time)
                until = int(end_dt.timestamp() * 1000)

            print(
                f"Collecting {timeframe} candles for {symbol} from {self.exchange_name}"
            )
            if start_time:
                print(f"Start time: {start_time}")
            if end_time:
                print(f"End time: {end_time}")

            all_candles = []
            current_since = since

            while True:
                # Fetch candles
                candles = self.exchange.fetch_ohlcv(
                    symbol=symbol, timeframe=timeframe, since=current_since, limit=limit
                )

                if not candles:
                    break

                # Filter candles by end time if specified
                if until:
                    candles = [c for c in candles if c[0] <= until]

                all_candles.extend(candles)
                print(f"Fetched {len(candles)} candles (Total: {len(all_candles)})")

                # Check if we've reached the end time or no more data
                if until and candles and candles[-1][0] >= until:
                    break

                if len(candles) < limit:
                    break

                # Update since for next batch
                current_since = candles[-1][0] + 1

                # Rate limiting
                time.sleep(self.exchange.rateLimit / 1000)

            if not all_candles:
                print("No candle data retrieved")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(
                all_candles,
                columns=["timestamp", "open", "high", "low", "close", "volume"],
            )

            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)

            # Remove duplicates and sort
            df = (
                df.drop_duplicates(subset=["timestamp"])
                .sort_values("timestamp")
                .reset_index(drop=True)
            )

            print(f"Successfully collected {len(df)} candles")
            print(
                f"Date range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}"
            )

            return df

        except Exception as e:
            print(f"Error collecting candles: {e}")
            raise

    def save_to_csv(
        self, df: pd.DataFrame, symbol: str, timeframe: str, output_dir: str = "data"
    ) -> str:
        """
        Save candle data to CSV file

        Args:
            df: DataFrame with candle data
            symbol: Trading pair symbol
            timeframe: Timeframe used
            output_dir: Directory to save the file

        Returns:
            Path to saved file
        """
        if df.empty:
            raise ValueError("DataFrame is empty, nothing to save")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename
        symbol_clean = symbol.replace("/", "_")
        start_date = df["timestamp"].iloc[0].strftime("%Y%m%d")
        end_date = df["timestamp"].iloc[-1].strftime("%Y%m%d")

        filename = f"{self.exchange_name}_{symbol_clean}_{timeframe}_{start_date}_{end_date}.csv"
        filepath = os.path.join(output_dir, filename)

        # Save to CSV
        df.to_csv(filepath, index=False)
        print(f"Data saved to: {filepath}")

        return filepath

    def collect_and_save(
        self,
        symbol: str,
        timeframe: str = "1h",
        start_time: str = "2025-08-05",
        end_time: str = "2025-08-06",
        output_dir: str = "data",
    ) -> str:
        """
        Collect candle data and save to CSV in one step

        Returns:
            Path to saved file
        """
        df = self.collect_candles(symbol, timeframe, start_time, end_time)
        if not df.empty:
            return self.save_to_csv(df, symbol, timeframe, output_dir)
        else:
            raise ValueError("No data collected")
