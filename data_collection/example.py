#!/usr/bin/env python3
"""
Example script showing how to use the CandleDataCollector
"""

from collector import CandleDataCollector


def main():
    """Example usage of the data collector"""

    # Initialize collector for Binance exchange
    collector = CandleDataCollector("binance")

    print("Available timeframes:", collector.get_available_timeframes())

    # Example 1: Collect recent BTC/USDT 1-hour data
    print("\n" + "=" * 50)
    print("Example 1: Collecting recent BTC/USDT 1h data")
    print("=" * 50)

    try:
        df = collector.collect_candles(
            symbol="BTC/USDT",
            timeframe="1h",
            limit=100,  # Last 100 candles
        )

        if not df.empty:
            print("\nData preview:")
            print(df.head())
            print(f"\nData shape: {df.shape}")

            # Save to CSV
            filepath = collector.save_to_csv(df, "BTC/USDT", "1h", "data")
            print(f"Saved to: {filepath}")

    except Exception as e:
        print(f"Error in example 1: {e}")

    # Example 2: Collect data for specific date range
    print("\n" + "=" * 50)
    print("Example 2: Collecting ETH/USDT data for specific date range")
    print("=" * 50)

    try:
        # Collect 5-minute data for a specific week
        filepath = collector.collect_and_save(
            symbol="ETH/USDT",
            timeframe="5m",
            start_time="2024-01-01",
            end_time="2024-01-07",
            output_dir="data",
        )
        print(f"Data collected and saved to: {filepath}")

    except Exception as e:
        print(f"Error in example 2: {e}")

    # Example 3: Show available symbols (first 20)
    print("\n" + "=" * 50)
    print("Example 3: Available trading symbols (first 20)")
    print("=" * 50)

    try:
        symbols = collector.get_available_symbols()
        print(f"Total symbols available: {len(symbols)}")
        print("First 20 symbols:")
        for i, symbol in enumerate(symbols[:20], 1):
            print(f"{i:2d}. {symbol}")

    except Exception as e:
        print(f"Error in example 3: {e}")


def demo_different_exchanges():
    """Demo with different exchanges"""
    exchanges = ["binance", "coinbase", "kraken"]

    print("\n" + "=" * 60)
    print("Demo: Different Exchanges")
    print("=" * 60)

    for exchange_name in exchanges:
        print(f"\n--- {exchange_name.upper()} ---")
        try:
            collector = CandleDataCollector(exchange_name)
            timeframes = collector.get_available_timeframes()
            print(f"Available timeframes: {timeframes}")

            # Try to get some symbols
            symbols = collector.get_available_symbols()
            if symbols:
                print(f"Number of symbols: {len(symbols)}")
                print(f"Sample symbols: {symbols[:5]}")

        except Exception as e:
            print(f"Error with {exchange_name}: {e}")


if __name__ == "__main__":
    main()

    # Uncomment to demo different exchanges
    # demo_different_exchanges()
