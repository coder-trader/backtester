"""
Backtester CLI using Typer with autocomplete functionality
"""

from pathlib import Path
from typing import List
import importlib
import inspect

import typer
from rich.console import Console
from rich.table import Table

from backtester import Backtester
from strategy.base import StrategyBase


app = typer.Typer(
    name="backtester",
    help="Cryptocurrency backtesting framework with strategy support",
    rich_markup_mode="rich",
)
console = Console()


def get_available_strategies() -> List[str]:
    """Get list of available strategy classes"""
    strategies = []
    strategy_dir = Path("strategy")

    if not strategy_dir.exists():
        return strategies

    for py_file in strategy_dir.glob("*.py"):
        if py_file.name.startswith("_") or py_file.name == "base.py":
            continue

        module_name = py_file.stem
        try:
            module = importlib.import_module(f"strategy.{module_name}")

            # Find strategy classes (subclasses of StrategyBase)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, StrategyBase)
                    and obj is not StrategyBase
                    and obj.__module__ == module.__name__
                ):
                    strategies.append(name)
        except Exception:
            continue

    return sorted(strategies)


def get_data_files() -> List[str]:
    """Get list of available CSV data files"""
    data_files = []

    # Check common data directories
    data_dirs = ["data", "data_collection/data", "../data", "."]

    for data_dir in data_dirs:
        data_path = Path(data_dir)
        if data_path.exists():
            for csv_file in data_path.glob("*.csv"):
                # Use the path as-is if it's already relative, otherwise make it relative
                try:
                    if csv_file.is_absolute():
                        relative_path = str(csv_file.relative_to(Path.cwd()))
                    else:
                        relative_path = str(csv_file)
                    data_files.append(relative_path)
                except ValueError:
                    # If relative_to fails, just use the path as-is
                    data_files.append(str(csv_file))

    return sorted(set(data_files))  # Remove duplicates


def strategy_autocomplete(incomplete: str) -> List[str]:
    """Autocomplete function for strategy names"""
    strategies = get_available_strategies()
    return [s for s in strategies if s.lower().startswith(incomplete.lower())]


def data_file_autocomplete(incomplete: str) -> List[str]:
    """Autocomplete function for data file paths"""
    files = get_data_files()
    return [f for f in files if incomplete.lower() in f.lower()]


def create_strategy_instance(
    strategy_name: str, initial_capital: float = 10000.0
) -> StrategyBase:
    """Create an instance of the specified strategy"""
    # Import the strategy module
    for py_file in Path("strategy").glob("*.py"):
        if py_file.name.startswith("_") or py_file.name == "base.py":
            continue

        module_name = py_file.stem
        try:
            module = importlib.import_module(f"strategy.{module_name}")

            # Find the strategy class
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    name == strategy_name
                    and issubclass(obj, StrategyBase)
                    and obj is not StrategyBase
                ):
                    # Get constructor parameters
                    sig = inspect.signature(obj.__init__)
                    params = list(sig.parameters.keys())[1:]  # Skip 'self'

                    # Create instance with initial_capital if supported
                    if "initial_capital" in params:
                        return obj(initial_capital=initial_capital)
                    else:
                        return obj()

        except Exception as e:
            console.print(f"[red]Error importing strategy {strategy_name}: {e}[/red]")
            continue

    raise ValueError(f"Strategy '{strategy_name}' not found")


@app.command("run")
def run_backtest(
    strategy: str = typer.Argument(
        ..., help="Strategy class name to use", autocompletion=strategy_autocomplete
    ),
    data_file: str = typer.Argument(
        ..., help="Path to CSV data file", autocompletion=data_file_autocomplete
    ),
    capital: float = typer.Option(
        10000.0, "--capital", "-c", help="Initial capital amount"
    ),
    show_trades: bool = typer.Option(
        True, "--show-trades/--no-trades", help="Show individual trades in results"
    ),
    max_trades: int = typer.Option(
        10, "--max-trades", "-n", help="Maximum number of trades to display"
    ),
):
    """
    Run a backtest with the specified strategy and data file.

    Example:
        python main.py run RSIStrategy data_collection/data/binance_BTC_USDT_1h_20240101_20240107.csv
    """
    console.print("[bold blue]🚀 Starting backtest[/bold blue]")
    console.print(f"Strategy: [green]{strategy}[/green]")
    console.print(f"Data file: [green]{data_file}[/green]")
    console.print(f"Initial capital: [green]${capital:,.2f}[/green]")

    try:
        # Check if data file exists
        if not Path(data_file).exists():
            console.print(f"[red]❌ Data file not found: {data_file}[/red]")
            raise typer.Exit(1)

        # Create strategy instance
        console.print("\n[yellow]📊 Initializing strategy...[/yellow]")
        strategy_instance = create_strategy_instance(strategy, capital)

        # Create backtester
        backtester = Backtester(strategy_instance)

        # Run backtest
        console.print("[yellow]⚡ Running backtest...[/yellow]")
        results = backtester.run(data_file)

        # Display results
        console.print("\n[bold green]✅ Backtest completed![/bold green]")

        # Create results table
        table = Table(
            title="Backtest Results", show_header=True, header_style="bold magenta"
        )
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("Initial Capital", f"${results.initial_capital:,.2f}")
        table.add_row("Final Value", f"${results.final_value:,.2f}")
        table.add_row("Total Return", f"{results.total_return_pct:.2f}%")
        table.add_row("Max Drawdown", f"{results.max_drawdown_pct:.2f}%")
        table.add_row("Total Trades", str(results.total_trades))
        table.add_row("Winning Trades", str(results.winning_trades))
        table.add_row("Losing Trades", str(results.losing_trades))
        table.add_row("Win Rate", f"{results.win_rate_pct:.2f}%")
        table.add_row("Average Win", f"${results.avg_win:.2f}")
        table.add_row("Average Loss", f"${results.avg_loss:.2f}")

        console.print(table)

        # Show trades if requested
        if show_trades and len(results.trades) > 0:
            console.print(
                f"\n[bold yellow]📋 Recent Trades (showing up to {max_trades}):[/bold yellow]"
            )
            trades_table = Table(show_header=True, header_style="bold magenta")
            trades_table.add_column("Timestamp", style="cyan")
            trades_table.add_column("Action", style="yellow")
            trades_table.add_column("Price", style="white")
            trades_table.add_column("P&L", style="white")

            for _, trade in results.trades.head(max_trades).iterrows():
                pnl_color = (
                    "green"
                    if trade["pnl"] > 0
                    else "red"
                    if trade["pnl"] < 0
                    else "white"
                )
                trades_table.add_row(
                    str(trade["timestamp"]),
                    trade["action"],
                    f"${trade['price']:.2f}",
                    f"[{pnl_color}]${trade['pnl']:.2f}[/{pnl_color}]",
                )

            console.print(trades_table)

    except Exception as e:
        console.print(f"[red]❌ Error running backtest: {e}[/red]")
        raise typer.Exit(1)


@app.command("list-strategies")
def list_strategies():
    """List all available trading strategies."""
    strategies = get_available_strategies()

    if not strategies:
        console.print("[yellow]No strategies found in the strategy directory.[/yellow]")
        return

    console.print("[bold blue]📊 Available Strategies:[/bold blue]\n")

    for i, strategy in enumerate(strategies, 1):
        console.print(f"{i:2d}. [green]{strategy}[/green]")

    console.print(f"\n[dim]Total: {len(strategies)} strategies[/dim]")


@app.command("list-data")
def list_data_files():
    """List all available CSV data files."""
    files = get_data_files()

    if not files:
        console.print("[yellow]No CSV data files found.[/yellow]")
        console.print(
            "[dim]Check directories: data/, data_collection/data/, ../data/[/dim]"
        )
        return

    console.print("[bold blue]📁 Available Data Files:[/bold blue]\n")

    for i, file_path in enumerate(files, 1):
        file_size = ""
        try:
            size_bytes = Path(file_path).stat().st_size
            if size_bytes < 1024:
                file_size = f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                file_size = f"{size_bytes / 1024:.1f}KB"
            else:
                file_size = f"{size_bytes / (1024 * 1024):.1f}MB"
        except:
            file_size = "?"

        console.print(f"{i:2d}. [green]{file_path}[/green] [dim]({file_size})[/dim]")

    console.print(f"\n[dim]Total: {len(files)} files[/dim]")


@app.command("info")
def show_info():
    """Show information about the backtester framework."""
    console.print("[bold blue]🔬 Backtester Framework Info[/bold blue]\n")

    # Show available strategies
    strategies = get_available_strategies()
    console.print(f"[yellow]Strategies available:[/yellow] {len(strategies)}")
    for strategy in strategies:
        console.print(f"  • {strategy}")

    print()

    # Show available data files
    files = get_data_files()
    console.print(f"[yellow]Data files available:[/yellow] {len(files)}")
    for file_path in files[:5]:  # Show first 5
        console.print(f"  • {file_path}")
    if len(files) > 5:
        console.print(f"  • ... and {len(files) - 5} more")

    print()
    console.print(
        "[dim]Use 'list-strategies' and 'list-data' for complete lists.[/dim]"
    )


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
