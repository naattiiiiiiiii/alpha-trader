# Alpha Trader

Autonomous stock trading agent powered by local LLMs and Alpaca paper trading.

- **Ollama (local LLM)** -- $0 cost, no API fees
- **Alpaca paper trading** -- $0, practice with real market data
- **Real-time news from Alpaca** -- sentiment analysis on live headlines

## Quick Start

```bash
# 1. Install Ollama (https://ollama.com)
ollama pull llama3.2

# 2. Clone and configure
git clone https://github.com/naattiiiiiiiii/alpha-trader.git
cd alpha-trader
cp .env.example .env   # Fill in your Alpaca API keys

# 3. Start the database
docker compose up db -d

# 4. Install dependencies
uv sync

# 5. Run
uv run python -m src.main
```

## Dashboard

Visit `http://localhost:8000` after starting.

## Configuration

Edit `.env` or use the Settings page in the dashboard.

## Paper Trading

Set `ALPACA_PAPER=true` in `.env` (default). Get free API keys at https://alpaca.markets.
