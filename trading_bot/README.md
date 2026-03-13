# Binance Futures Testnet Trading Bot

A simplified Python trading bot for placing orders on Binance Futures Testnet (USDT-M).

## Features

- **Market Orders** - Execute immediate buy/sell orders at current market price
- **Limit Orders** - Place orders at a specific price
- **Stop Market Orders** - Place stop-loss orders (bonus feature)
- **Beautiful CLI** - Rich terminal interface with colored output
- **Comprehensive Logging** - All API requests/responses logged to file
- **Input Validation** - Validates all parameters before submission
- **Error Handling** - Graceful handling of API and network errors

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py         # Package initialization
│   ├── client.py           # Binance API client wrapper
│   ├── orders.py           # Order placement logic
│   ├── validators.py       # Input validation
│   └── logging_config.py   # Logging configuration
├── logs/                   # Log files (auto-created)
├── cli.py                  # CLI entry point
├── env.example.txt         # Environment variables template
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### 2. Clone/Download the Repository

```bash
cd trading_bot
```

### 3. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API Credentials

1. **Register for Binance Futures Testnet**: https://testnet.binancefuture.com
2. **Generate API credentials** from the testnet dashboard
3. **Create `.env` file** in the project root:

```bash
# Copy the example file (Windows)
copy env.example.txt .env

# Copy the example file (Linux/Mac)
cp env.example.txt .env

# Edit with your credentials
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

**Alternative**: Set environment variables directly:

```bash
# Windows (PowerShell)
$env:BINANCE_API_KEY="your_api_key"
$env:BINANCE_API_SECRET="your_api_secret"

# Linux/Mac
export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"
```

## Usage

### Get Help

```bash
python cli.py --help
python cli.py order --help
```

### Place a Market Order

```bash
# Buy 0.001 BTC at market price
python cli.py order BTCUSDT BUY MARKET 0.001

# Sell 0.001 BTC at market price
python cli.py order BTCUSDT SELL MARKET 0.001

# Skip confirmation prompt
python cli.py order BTCUSDT BUY MARKET 0.001 --no-confirm
```

### Place a Limit Order

```bash
# Buy 0.001 BTC at $50,000
python cli.py order BTCUSDT BUY LIMIT 0.001 --price 50000

# Sell 0.001 BTC at $100,000
python cli.py order BTCUSDT SELL LIMIT 0.001 --price 100000

# Short form
python cli.py order BTCUSDT BUY LIMIT 0.001 -p 50000
```

### Place a Stop Market Order (Bonus)

```bash
# Stop-loss: Sell 0.001 BTC if price drops to $40,000
python cli.py order BTCUSDT SELL STOP_MARKET 0.001 --stop-price 40000

# Stop-buy: Buy 0.001 BTC if price rises to $60,000
python cli.py order BTCUSDT BUY STOP_MARKET 0.001 -sp 60000
```

### Check Current Price

```bash
python cli.py price BTCUSDT
```

### View Account Information

```bash
python cli.py account
```

### View Open Orders

```bash
# All open orders
python cli.py open-orders

# Filter by symbol
python cli.py open-orders --symbol BTCUSDT
```

## Example Output

### Market Order

```
+-------------- Trading Bot ---------------+
|    Binance Futures Testnet Trading Bot   |
+------------------------------------------+

+-------- Order Request Summary -----------+
| Symbol      BTCUSDT                      |
| Side        BUY                          |
| Type        MARKET                       |
| Quantity    0.001                        |
+------------------------------------------+

Do you want to place this order? [y/n]: y

+------- [OK] Order Placed Successfully -------+
| Order ID       12345678                      |
| Symbol         BTCUSDT                       |
| Side           BUY                           |
| Type           MARKET                        |
| Status         FILLED                        |
| Quantity       0.001                         |
| Executed Qty   0.001                         |
| Avg Price      50000.00                      |
+----------------------------------------------+

[OK] Order placed successfully!
```

## Logging

All API activity is logged to the `logs/` directory:

- **File**: `logs/trading_bot_YYYYMMDD.log`
- **Format**: `timestamp | level | logger | message`
- **Includes**: API requests, responses, errors, and order details

### Sample Log Output

```
2026-03-13 10:30:00 | INFO     | trading_bot | API Request: POST /fapi/v1/order
2026-03-13 10:30:00 | INFO     | trading_bot | Placing MARKET BUY order: 0.001 BTCUSDT
2026-03-13 10:30:01 | INFO     | trading_bot | API Response: Status 200
2026-03-13 10:30:01 | INFO     | trading_bot | MARKET order placed successfully: ID=12345678, Status=FILLED
```

## Assumptions

1. **Testnet Only**: This bot is designed for Binance Futures Testnet only. Do not use with real credentials.

2. **USDT-M Futures**: The bot uses USDT-margined futures contracts.

3. **Symbol Format**: Symbols should be in standard Binance format (e.g., `BTCUSDT`, `ETHUSDT`).

4. **Minimum Quantities**: Binance has minimum order quantities. For BTCUSDT, minimum is typically 0.001.

5. **Time in Force**: Limit orders use GTC (Good Till Cancelled) by default.

6. **No Position Management**: This bot places orders but does not manage positions or implement trading strategies.

## Error Handling

The bot handles various error scenarios:

| Error Type | Handling |
|------------|----------|
| Invalid input | Validation error with clear message |
| API errors | Displays error code and message from Binance |
| Network failures | Logs error and displays user-friendly message |
| Missing credentials | Prompts user to configure API keys |

## Supported Order Types

| Type | Description | Required Parameters |
|------|-------------|---------------------|
| MARKET | Execute at current price | symbol, side, quantity |
| LIMIT | Execute at specified price | symbol, side, quantity, price |
| STOP_MARKET | Triggered market order | symbol, side, quantity, stop_price |

## Dependencies

- **typer** - CLI framework
- **requests** - HTTP client
- **python-dotenv** - Environment variable management
- **rich** - Beautiful terminal output

## Troubleshooting

### "API credentials not found"

Ensure your `.env` file exists and contains valid credentials:

```bash
cat .env  # Check file contents (Linux/Mac)
type .env  # Check file contents (Windows)
```

### "Invalid symbol format"

Use uppercase symbols without spaces: `BTCUSDT`, not `btc usdt` or `BTC/USDT`.

### "Quantity too small"

Check Binance's minimum order quantity for the symbol. Most symbols require at least 0.001.

### "Price is required for LIMIT orders"

Add the `--price` flag for limit orders:

```bash
python cli.py order BTCUSDT BUY LIMIT 0.001 --price 50000
```

## License

MIT License - Feel free to use and modify for your needs.

---

**Note**: This is a testnet bot for educational/demonstration purposes. Always test thoroughly before using any trading bot with real funds.
