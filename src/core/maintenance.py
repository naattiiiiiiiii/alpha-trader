import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

RETENTION_DAYS = {
    "snapshots": 90,
    "logs": 30,
    "signals": 180,
    "trades": None,  # Keep forever
}


def get_cleanup_cutoff(data_type: str, now: datetime | None = None) -> datetime:
    now = now or datetime.utcnow()
    days = RETENTION_DAYS.get(data_type)
    if days is None:
        raise ValueError(f"No retention policy for {data_type}")
    return now - timedelta(days=days)


def should_alert_no_cycles(
    last_cycle: datetime, now: datetime, market_open: bool
) -> bool:
    if not market_open:
        return False
    elapsed = (now - last_cycle).total_seconds() / 60
    return elapsed > 30


@dataclass
class HealthStatus:
    alpaca: bool = False
    claude: bool = False
    database: bool = False
    telegram: bool = False

    @property
    def is_healthy(self) -> bool:
        return all([self.alpaca, self.claude, self.database, self.telegram])

    @property
    def failed_components(self) -> list[str]:
        failed = []
        if not self.alpaca:
            failed.append("alpaca")
        if not self.claude:
            failed.append("claude")
        if not self.database:
            failed.append("database")
        if not self.telegram:
            failed.append("telegram")
        return failed


async def check_component_health(component: str) -> bool:
    """Check if a component is reachable. Returns True if healthy."""
    try:
        if component == "alpaca":
            from src.core.executor import Executor
            from src.config import get_settings
            settings = get_settings()
            executor = Executor(paper=settings.alpaca_paper)
            executor.get_account()
            return True
        elif component == "claude":
            import anthropic
            from src.config import get_settings
            settings = get_settings()
            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            # Minimal ping
            await client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True
        elif component == "database":
            from src.models.database import engine
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        elif component == "telegram":
            from src.config import get_settings
            settings = get_settings()
            if not settings.telegram_bot_token:
                return True  # Not configured = not a failure
            from telegram import Bot
            bot = Bot(token=settings.telegram_bot_token)
            await bot.get_me()
            return True
    except Exception as e:
        logger.warning(f"Health check failed for {component}: {e}")
        return False
    return False


async def run_data_cleanup(session):
    """Delete old data based on retention policies."""
    from src.models import PortfolioSnapshot, RiskEvent, Signal
    from sqlalchemy import delete

    now = datetime.utcnow()

    for model, data_type in [
        (PortfolioSnapshot, "snapshots"),
        (RiskEvent, "logs"),
        (Signal, "signals"),
    ]:
        cutoff = get_cleanup_cutoff(data_type, now)
        stmt = delete(model).where(model.timestamp < cutoff)
        result = await session.execute(stmt)
        if result.rowcount > 0:
            logger.info(f"Cleaned up {result.rowcount} old {data_type} records")

    await session.commit()
