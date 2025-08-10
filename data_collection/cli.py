#!/usr/bin/env python3
"""
Command-line interface for collecting candle data
"""

import argparse
import sys
from collector import CandleDataCollector


def main():
    parser = argparse.ArgumentParser(
        description="Collect cryptocurrency candle data using CCXT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect last 100 BTC/USDT 1-hour candles from Binance
  python cli.py BTC/USDT -t 1h

  # Collect ETH/USDT 5-minute data for specific date range
  python cli.py ETH/USDT -t 5m -s "2024-01-01" -e "2024-01-07"
  
  # Use different exchange
  python cli.py BTC/USD -x coinbase -t 1d -s "2024-01-01"
  
  # List available symbols for an exchange
  python cli.py --list-symbols -x kraken
  
  # List available timeframes for an exchange
  python cli.py --list-timeframes -x binance
        """,
    )

    parser.add_argument(
        "symbol", nargs="?", help="Trading pair symbol (e.g., BTC/USDT)"
    )
    parser.add_argument(
        "-x", "--exchange", default="binance", help="Exchange name (default: binance)"
    )
    parser.add_argument(
        "-t",
        "--timeframe",
        default="1h",
        help="Timeframe (default: 1h). Examples: 1m, 5m, 15m, 1h, 4h, 1d",
    )
    parser.add_argument(
        "-s",
        "--start-time",
        help='Start time (e.g., "2024-01-01", "2024-01-01 12:00:00")',
    )
    parser.add_argument(
        "-e", "--end-time", help='End time (e.g., "2024-01-31", "2024-01-31 23:59:59")'
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=1000,
        help="Maximum candles per request (default: 1000)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="data",
        help="Output directory for CSV files (default: data)",
    )
    parser.add_argument(
        "--list-symbols", action="store_true", help="List available trading symbols"
    )
    parser.add_argument(
        "--list-timeframes", action="store_true", help="List available timeframes"
    )

    args = parser.parse_args()

    # Initialize collector
    try:
        collector = CandleDataCollector(args.exchange)
        print(f"Initialized {args.exchange} exchange")
    except Exception as e:
        print(f"Error initializing exchange '{args.exchange}': {e}")
        return 1

    # Handle list operations
    if args.list_symbols:
        print(f"\nAvailable symbols on {args.exchange}:")
        try:
            symbols = collector.get_available_symbols()
            print(f"Total: {len(symbols)} symbols")

            # Show first 50 symbols
            for i, symbol in enumerate(symbols[:50], 1):
                print(f"{i:3d}. {symbol}")

            if len(symbols) > 50:
                print(f"... and {len(symbols) - 50} more")

        except Exception as e:
            print(f"Error listing symbols: {e}")
            return 1
        return 0

    if args.list_timeframes:
        print(f"\nAvailable timeframes on {args.exchange}:")
        try:
            timeframes = collector.get_available_timeframes()
            for i, tf in enumerate(timeframes, 1):
                print(f"{i:2d}. {tf}")
        except Exception as e:
            print(f"Error listing timeframes: {e}")
            return 1
        return 0

    # Validate required arguments
    if not args.symbol:
        print(
            "Error: Symbol is required when not using --list-symbols or --list-timeframes"
        )
        parser.print_help()
        return 1

    # Collect data
    print("\nCollecting data...")
    print(f"Exchange: {args.exchange}")
    print(f"Symbol: {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    if args.start_time:
        print(f"Start time: {args.start_time}")
    if args.end_time:
        print(f"End time: {args.end_time}")
    print(f"Output directory: {args.output_dir}")

    try:
        filepath = collector.collect_and_save(
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_time=args.start_time,
            end_time=args.end_time,
            output_dir=args.output_dir,
        )

        print(f"\n✅ Success! Data saved to: {filepath}")

        # Show basic stats
        import pandas as pd

        df = pd.read_csv(filepath)
        print("\nData Summary:")
        print(f"  Candles: {len(df)}")
        print(f"  Date range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
        print(f"  Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")

        return 0

    except Exception as e:
        print(f"\n❌ Error collecting data: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
