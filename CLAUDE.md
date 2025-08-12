# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive cryptocurrency backtesting framework with three main components working together:

1. **Data Collection System** (`data_collection/`): CCXT-based cryptocurrency data collection from exchanges
2. **Strategy Development Framework** (`strategy/`): Abstract base classes for implementing trading strategies  
3. **Backtesting Engine** (`backtester.py`): Core backtesting logic with performance analysis

The framework uses a dataclass-based architecture with `BacktestResults` for type-safe results handling.

## Key Commands

### Environment Setup
```bash
uv sync  # Install all dependencies including TA-Lib, CCXT, Typer
```

### Data Collection
```bash
# Using Makefile (recommended)
cd data_collection
make collect SYMBOL=BTC/USDT TIMEFRAME=1h START=2024-01-01 END=2024-01-07
make list-symbols EXCHANGE=binance
make btc  # Quick BTC/USDT collection

# Direct CLI usage
uv run python data_collection/cli.py BTC/USDT -t 1h -s "2024-01-01" -e "2024-01-07"
```

### Running Backtests
```bash
# Main CLI with autocomplete (Typer-based)
uv run python main.py run RSIStrategy data_collection/data/binance_BTC_USDT_1h_20240101_20240107.csv
uv run python main.py list-strategies
uv run python main.py list-data

# With custom parameters
uv run python main.py run RSIStrategy data.csv --capital 50000 --show-trades --max-trades 20
```

## Architecture Deep Dive

### Strategy Pattern Implementation
- `StrategyBase` is an abstract base class requiring `on_tick(data, indicators) -> Optional[str]` implementation
- Strategies receive OHLCV data as `pd.Series` and indicators as `Dict[str, float]`
- Must return trading signals: `'buy'`, `'sell'`, `'close'`, or `None`
- Built-in position tracking (`self.position`: 0=flat, 1=long, -1=short) and trade management
- Risk management through `execute_trade()` method handles position transitions automatically

### Backtesting Engine Flow
1. **Data Loading**: CSV parsing with automatic timestamp handling and column standardization
2. **Indicator Calculation**: TA-Lib integration via `calculate_indicators_at_index()` using historical lookback
3. **Strategy Execution**: Calls `strategy.on_tick()` for each candle with current data + indicators
4. **Trade Processing**: `execute_trade()` manages position changes and P&L calculation
5. **Results Generation**: Returns `BacktestResults` dataclass with comprehensive performance metrics

### Data Collection Architecture
- `CandleDataCollector` wraps CCXT exchange APIs with rate limiting
- Handles pagination for large date ranges automatically
- Validates symbols/timeframes against exchange capabilities before fetching
- Processes raw OHLCV arrays into clean pandas DataFrames with UTC timestamps
- Built-in deduplication and chronological sorting

### CLI System
- Main CLI (`main.py`) uses Typer with Rich formatting and autocomplete
- Strategy autocomplete dynamically discovers classes in `strategy/` folder
- Data file autocomplete scans multiple directories for CSV files
- Separate data collection CLI (`data_collection/cli.py`) with argparse

## Strategy Development

### Creating New Strategies
1. Inherit from `StrategyBase` in `strategy/` folder
2. Implement `on_tick(self, data: pd.Series, indicators: Dict[str, float]) -> Optional[str]`
3. Access current OHLCV data via `data['close']`, `data['high']`, etc.
4. Use indicators like `indicators.get('rsi', 50.0)`, `indicators.get('sma_20')`
5. Return signals: `'buy'` (go long), `'sell'` (go short), `'close'` (exit position), `None` (hold)
6. Strategy automatically appears in CLI autocomplete

### Risk Management Pattern
Current strategies implement take profit/stop loss via P&L percentage calculation:
```python
if self.position != 0:
    pnl_pct = self._calculate_pnl_percentage(current_price)
    if pnl_pct >= self.take_profit_pct:
        return 'close'  # Take profit
    elif pnl_pct <= -self.stop_loss_pct:
        return 'close'  # Stop loss
```

## Data Flow

1. **Raw Data**: Exchange APIs → CCXT → CSV files (OHLCV format)
2. **Backtesting**: CSV → DataFrame → Indicators (TA-Lib) → Strategy signals → Trade execution → Results
3. **Output**: `BacktestResults` dataclass with equity curve, trade log, and performance metrics

## Dependencies & External APIs
- **TA-Lib**: Technical indicators (requires system-level installation)
- **CCXT**: Exchange connectivity (100+ exchanges supported)
- **Typer + Rich**: CLI with autocomplete and styled output
- **pandas**: Data manipulation with UTC timestamp handling

## File Organization
- `strategy/`: All trading strategies inherit from `StrategyBase`
- `data_collection/`: Independent module for fetching exchange data
- `diagrams/`: Mermaid flow charts for complex methods
- `data/` and `data_collection/data/`: CSV storage for historical data
- `main.py`: Primary CLI entry point for backtesting
- `backtester.py`: Core backtesting engine with `BacktestResults` output