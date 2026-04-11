import asyncio
import logging
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.config import get_settings
from src.agents.technical import TechnicalAgent
from src.agents.fundamental import FundamentalAgent
from src.agents.sentiment import SentimentAgent
from src.agents.decision import DecisionAgent
from src.agents.risk import RiskAgent
from src.core.portfolio import PortfolioManager
from src.core.executor import Executor
from src.core.scheduler import AnalysisCycle

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("alpha-trader")

# Default watchlist
DEFAULT_WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "JNJ",
    "WMT", "PG", "UNH", "HD", "MA", "DIS", "NFLX", "PYPL", "ADBE", "CRM",
]


async def main():
    settings = get_settings()
    logger.info("Alpha Trader starting...")

    # Initialize components
    technical = TechnicalAgent()
    fundamental = FundamentalAgent()
    sentiment = SentimentAgent(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model_fast,
    )
    decision = DecisionAgent(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model_smart,
    )
    risk = RiskAgent(
        max_risk_per_trade=settings.max_risk_per_trade,
        max_daily_loss=settings.max_daily_loss,
        max_portfolio_heat=settings.max_portfolio_heat,
        max_drawdown=settings.max_drawdown,
        max_sector_exposure=settings.max_sector_exposure,
        max_consecutive_losses=settings.max_consecutive_losses,
        min_rr_ratio=settings.min_rr_ratio,
    )
    portfolio = PortfolioManager(initial_equity=100_000)
    executor = Executor(paper=settings.alpaca_paper)

    cycle = AnalysisCycle(
        technical=technical,
        fundamental=fundamental,
        sentiment=sentiment,
        decision=decision,
        risk=risk,
        portfolio=portfolio,
        executor=executor,
    )

    # Sync account on startup
    try:
        account = executor.get_account()
        portfolio.update_from_account(
            equity=account["equity"],
            cash=account["cash"],
            buying_power=account["buying_power"],
        )
        logger.info(f"Account synced: equity=${account['equity']:,.2f}")
    except Exception as e:
        logger.error(f"Failed to sync account: {e}")

    # Setup scheduler
    scheduler = AsyncIOScheduler()

    # Analysis cycle every N minutes during market hours (9:30-16:00 ET, Mon-Fri)
    scheduler.add_job(
        run_analysis_cycle,
        IntervalTrigger(minutes=settings.analysis_interval_minutes),
        args=[cycle, DEFAULT_WATCHLIST, executor, portfolio],
        id="analysis_cycle",
        name="Main analysis cycle",
    )

    # Daily reset at market open
    scheduler.add_job(
        portfolio.reset_daily,
        CronTrigger(hour=9, minute=30, timezone="US/Eastern", day_of_week="mon-fri"),
        id="daily_reset",
        name="Daily P&L reset",
    )

    scheduler.start()
    logger.info(f"Scheduler started. Analysis every {settings.analysis_interval_minutes}min.")

    # Start FastAPI in background
    import uvicorn
    from src.api.app import create_app

    app = create_app(portfolio=portfolio, executor=executor)
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    # Run server as a task
    server_task = asyncio.create_task(server.serve())
    logger.info("Dashboard running at http://0.0.0.0:8000")

    # Keep running
    stop_event = asyncio.Event()

    def shutdown(sig):
        logger.info(f"Received {sig}, shutting down...")
        stop_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown, sig)

    await stop_event.wait()
    scheduler.shutdown()
    server_task.cancel()
    logger.info("Alpha Trader stopped.")


async def run_analysis_cycle(cycle, watchlist, executor, portfolio):
    """Run one full analysis cycle across all watchlist symbols."""
    settings = get_settings()
    logger.info(f"Starting analysis cycle for {len(watchlist)} symbols...")

    # Sync account state
    try:
        account = executor.get_account()
        portfolio.update_from_account(
            equity=account["equity"],
            cash=account["cash"],
            buying_power=account["buying_power"],
        )
    except Exception as e:
        logger.error(f"Account sync failed: {e}")
        return

    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    from datetime import datetime, timedelta

    data_client = StockHistoricalDataClient(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
    )

    for symbol in watchlist:
        try:
            # Fetch historical bars
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Hour,
                start=datetime.now() - timedelta(days=30),
            )
            bars = data_client.get_stock_bars(request)
            df = bars[symbol].df if symbol in bars else None

            if df is None or len(df) < 50:
                logger.warning(f"{symbol}: insufficient data ({len(df) if df is not None else 0} bars)")
                continue

            result = await cycle.run_for_symbol(symbol, df)
            if result["action"] != "HOLD":
                logger.info(f"TRADE: {result['action']} {symbol} — {result['reason']}")
            else:
                logger.debug(f"{symbol}: HOLD — {result['reason']}")

        except Exception as e:
            logger.error(f"{symbol}: analysis failed — {e}")


if __name__ == "__main__":
    asyncio.run(main())
