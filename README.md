# Alpha Trader

Autonomous stock trading agent with professional 5-level risk management.

## Quick Start

```bash
# Clone and install
git clone https://github.com/naattiiiiii/alpha-trader.git
cd alpha-trader
cp .env.example .env  # Fill in your API keys
uv sync

# Run with Docker
docker compose up

# Or run directly
uv run python -m src.main
```

## Dashboard

Visit `http://localhost:8000` after starting.

## Configuration

Edit `.env` or use the Settings page in the dashboard.

## Paper Trading

Set `ALPACA_PAPER=true` in `.env` (default). Get API keys at https://alpaca.markets.
