"""
CLI entry point for the Trading Bot.
Provides command-line interface for placing orders on Binance Futures Testnet.
"""

import os
import sys
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from bot.client import BinanceClient, BinanceAPIError
from bot.orders import OrderManager, OrderResult
from bot.logging_config import setup_logging, get_logger
from bot.validators import ValidationError

# Load environment variables
load_dotenv()

# Initialize Rich console for beautiful output
# Force UTF-8 encoding for Windows compatibility
console = Console(force_terminal=True, legacy_windows=False)

# Create Typer app
app = typer.Typer(
    name="trading-bot",
    help="Binance Futures Testnet Trading Bot",
    add_completion=False,
    rich_markup_mode="rich"
)


def get_client() -> BinanceClient:
    """
    Initialize and return Binance client with API credentials.
    
    Raises:
        typer.Exit: If credentials are not configured
    """
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        console.print(Panel(
            "[red bold]API credentials not found![/red bold]\n\n"
            "Please set the following environment variables:\n"
            "  - BINANCE_API_KEY\n"
            "  - BINANCE_API_SECRET\n\n"
            "Or create a [cyan].env[/cyan] file with these values.",
            title="[!] Configuration Error",
            border_style="red"
        ))
        raise typer.Exit(1)
    
    return BinanceClient(api_key, api_secret)


def print_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None
) -> None:
    """Print a formatted order request summary."""
    table = Table(
        title="Order Request Summary",
        box=box.ROUNDED,
        show_header=False,
        title_style="bold cyan"
    )
    table.add_column("Field", style="dim")
    table.add_column("Value", style="bold")
    
    table.add_row("Symbol", symbol)
    table.add_row("Side", f"[green]{side}[/green]" if side == "BUY" else f"[red]{side}[/red]")
    table.add_row("Type", order_type)
    table.add_row("Quantity", quantity)
    
    if price:
        table.add_row("Price", price)
    if stop_price:
        table.add_row("Stop Price", stop_price)
    
    console.print()
    console.print(table)


def print_order_result(result: OrderResult) -> None:
    """Print a formatted order result."""
    if result.success:
        table = Table(
            title="[OK] Order Placed Successfully",
            box=box.ROUNDED,
            show_header=False,
            title_style="bold green"
        )
        table.add_column("Field", style="dim")
        table.add_column("Value", style="bold")
        
        table.add_row("Order ID", str(result.order_id))
        table.add_row("Symbol", result.symbol or "N/A")
        table.add_row("Side", 
            f"[green]{result.side}[/green]" if result.side == "BUY" 
            else f"[red]{result.side}[/red]"
        )
        table.add_row("Type", result.order_type or "N/A")
        table.add_row("Status", f"[yellow]{result.status}[/yellow]")
        table.add_row("Quantity", result.quantity or "N/A")
        table.add_row("Executed Qty", result.executed_qty or "0")
        
        if result.price and result.price != "0":
            table.add_row("Price", result.price)
        if result.avg_price and result.avg_price != "0":
            table.add_row("Avg Price", result.avg_price)
        
        console.print()
        console.print(table)
        console.print()
        console.print("[green][OK][/green] Order placed successfully!")
    else:
        console.print()
        console.print(Panel(
            f"[red]{result.error_message}[/red]",
            title="[X] Order Failed",
            border_style="red"
        ))


@app.command("order")
def place_order(
    symbol: str = typer.Argument(
        ...,
        help="Trading pair symbol (e.g., BTCUSDT)"
    ),
    side: str = typer.Argument(
        ...,
        help="Order side: BUY or SELL"
    ),
    order_type: str = typer.Argument(
        ...,
        help="Order type: MARKET, LIMIT, or STOP_MARKET"
    ),
    quantity: str = typer.Argument(
        ...,
        help="Order quantity"
    ),
    price: Optional[str] = typer.Option(
        None,
        "--price", "-p",
        help="Limit price (required for LIMIT orders)"
    ),
    stop_price: Optional[str] = typer.Option(
        None,
        "--stop-price", "-sp",
        help="Stop trigger price (required for STOP_MARKET orders)"
    ),
    confirm: bool = typer.Option(
        True,
        "--confirm/--no-confirm", "-y",
        help="Confirm before placing order"
    )
) -> None:
    """
    Place an order on Binance Futures Testnet.
    
    Examples:
        
        # Market buy order
        python cli.py order BTCUSDT BUY MARKET 0.001
        
        # Limit sell order
        python cli.py order BTCUSDT SELL LIMIT 0.001 --price 50000
        
        # Stop market order
        python cli.py order BTCUSDT SELL STOP_MARKET 0.001 --stop-price 40000
    """
    # Setup logging
    setup_logging()
    logger = get_logger()
    
    # Print header
    console.print()
    console.print(Panel(
        "[bold]Binance Futures Testnet Trading Bot[/bold]",
        title="Trading Bot",
        border_style="cyan"
    ))
    
    # Normalize inputs
    symbol = symbol.upper()
    side = side.upper()
    order_type = order_type.upper().replace("-", "_")
    
    # Print order summary
    print_order_summary(symbol, side, order_type, quantity, price, stop_price)
    
    # Confirm if needed
    if confirm:
        console.print()
        if not typer.confirm("Do you want to place this order?"):
            console.print("[yellow]Order cancelled.[/yellow]")
            raise typer.Exit(0)
    
    # Initialize client and order manager
    try:
        client = get_client()
        order_manager = OrderManager(client)
        
        # Log the order attempt
        logger.info(
            f"CLI order request: {order_type} {side} {quantity} {symbol}"
            + (f" @ {price}" if price else "")
            + (f" (stop: {stop_price})" if stop_price else "")
        )
        
        # Place the order
        with console.status("[bold cyan]Placing order...[/bold cyan]"):
            result = order_manager.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price
            )
        
        # Print result
        print_order_result(result)
        
        # Exit with appropriate code
        if not result.success:
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"CLI error: {e}")
        console.print(Panel(
            f"[red]{str(e)}[/red]",
            title="[X] Error",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.command("price")
def get_price(
    symbol: str = typer.Argument(
        ...,
        help="Trading pair symbol (e.g., BTCUSDT)"
    )
) -> None:
    """
    Get current price for a symbol.
    
    Example:
        python cli.py price BTCUSDT
    """
    setup_logging()
    
    try:
        client = get_client()
        symbol = symbol.upper()
        
        with console.status(f"[bold cyan]Fetching price for {symbol}...[/bold cyan]"):
            response = client.get_symbol_price(symbol)
        
        price = response.get("price", "N/A")
        
        console.print()
        console.print(Panel(
            f"[bold green]{price}[/bold green]",
            title=f"{symbol} Price",
            border_style="green"
        ))
        
    except BinanceAPIError as e:
        console.print(Panel(
            f"[red]{e.message}[/red]",
            title="[X] API Error",
            border_style="red"
        ))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(
            f"[red]{str(e)}[/red]",
            title="[X] Error",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.command("account")
def get_account() -> None:
    """
    Get account information.
    
    Example:
        python cli.py account
    """
    setup_logging()
    
    try:
        client = get_client()
        
        with console.status("[bold cyan]Fetching account info...[/bold cyan]"):
            account = client.get_account_info()
        
        # Create balance table
        table = Table(
            title="Account Balances",
            box=box.ROUNDED,
            title_style="bold cyan"
        )
        table.add_column("Asset", style="bold")
        table.add_column("Wallet Balance", justify="right")
        table.add_column("Available", justify="right", style="green")
        
        for asset in account.get("assets", []):
            wallet_balance = float(asset.get("walletBalance", 0))
            if wallet_balance > 0:
                table.add_row(
                    asset.get("asset", "N/A"),
                    f"{wallet_balance:.4f}",
                    f"{float(asset.get('availableBalance', 0)):.4f}"
                )
        
        console.print()
        console.print(table)
        
    except BinanceAPIError as e:
        console.print(Panel(
            f"[red]{e.message}[/red]",
            title="[X] API Error",
            border_style="red"
        ))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(
            f"[red]{str(e)}[/red]",
            title="[X] Error",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.command("open-orders")
def get_open_orders(
    symbol: Optional[str] = typer.Option(
        None,
        "--symbol", "-s",
        help="Filter by symbol"
    )
) -> None:
    """
    Get all open orders.
    
    Example:
        python cli.py open-orders
        python cli.py open-orders --symbol BTCUSDT
    """
    setup_logging()
    
    try:
        client = get_client()
        
        with console.status("[bold cyan]Fetching open orders...[/bold cyan]"):
            orders = client.get_open_orders(symbol.upper() if symbol else None)
        
        if not orders:
            console.print()
            console.print("[yellow]No open orders found.[/yellow]")
            return
        
        # Create orders table
        table = Table(
            title="Open Orders",
            box=box.ROUNDED,
            title_style="bold cyan"
        )
        table.add_column("Order ID", style="dim")
        table.add_column("Symbol")
        table.add_column("Side")
        table.add_column("Type")
        table.add_column("Price", justify="right")
        table.add_column("Quantity", justify="right")
        table.add_column("Status")
        
        for order in orders:
            side = order.get("side", "N/A")
            side_styled = f"[green]{side}[/green]" if side == "BUY" else f"[red]{side}[/red]"
            
            table.add_row(
                str(order.get("orderId", "N/A")),
                order.get("symbol", "N/A"),
                side_styled,
                order.get("type", "N/A"),
                order.get("price", "N/A"),
                order.get("origQty", "N/A"),
                order.get("status", "N/A")
            )
        
        console.print()
        console.print(table)
        
    except BinanceAPIError as e:
        console.print(Panel(
            f"[red]{e.message}[/red]",
            title="[X] API Error",
            border_style="red"
        ))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(
            f"[red]{str(e)}[/red]",
            title="[X] Error",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.callback()
def main() -> None:
    """
    Binance Futures Testnet Trading Bot
    
    A CLI tool for placing orders on Binance Futures Testnet.
    
    Setup:
        1. Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables
        2. Or create a .env file with these values
    
    Examples:
        python cli.py order BTCUSDT BUY MARKET 0.001
        python cli.py order BTCUSDT SELL LIMIT 0.001 --price 50000
        python cli.py price BTCUSDT
        python cli.py account
    """
    pass


if __name__ == "__main__":
    app()
