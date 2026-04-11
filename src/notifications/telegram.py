import logging
from telegram import Bot

from src.config import get_settings

logger = logging.getLogger(__name__)


def format_trade_message(
    action: str, symbol: str, qty: int = 0, price: float = 0,
    stop_loss: float = 0, take_profit: float = 0,
    reasoning: str = "", pnl: float = 0, pnl_pct: float = 0,
) -> str:
    if action in ("BUY", "SELL"):
        return (
            f"{'🟢' if action == 'BUY' else '🔴'} {action} {qty} {symbol} @ ${price:.2f}\n"
            f"SL: ${stop_loss:.2f} | TP: ${take_profit:.2f}\n"
            f"Razon: {reasoning}"
        )
    elif action == "STOP-LOSS":
        return (
            f"⛔ STOP-LOSS {symbol} @ ${price:.2f}\n"
            f"P&L: -${abs(pnl):.2f} ({pnl_pct:+.1f}%)"
        )
    elif action == "CLOSED":
        emoji = "✅" if pnl >= 0 else "❌"
        return (
            f"{emoji} CLOSED {symbol} @ ${price:.2f}\n"
            f"P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)"
        )
    return f"{action} {symbol}"


def format_daily_summary(
    trades_count: int, wins: int, losses: int,
    daily_pnl: float, equity: float, drawdown_pct: float,
) -> str:
    win_rate = (wins / trades_count * 100) if trades_count > 0 else 0
    return (
        f"📊 Resumen del dia\n"
        f"Trades: {trades_count} ({wins}W / {losses}L)\n"
        f"Win rate: {win_rate:.0f}%\n"
        f"P&L dia: ${daily_pnl:+.2f}\n"
        f"Equity: ${equity:,.2f}\n"
        f"Drawdown: {drawdown_pct:.1f}%"
    )


def format_circuit_breaker(level: str, drawdown_pct: float, action: str) -> str:
    return (
        f"🚨 CIRCUIT BREAKER {level}\n"
        f"Drawdown: {drawdown_pct:.1f}%\n"
        f"Accion: {action}"
    )


class TelegramNotifier:
    def __init__(self, token: str = "", chat_id: str = ""):
        settings = get_settings()
        self._token = token or settings.telegram_bot_token
        self._chat_id = chat_id or settings.telegram_chat_id
        self._bot: Bot | None = None

    async def _get_bot(self) -> Bot:
        if self._bot is None:
            self._bot = Bot(token=self._token)
        return self._bot

    async def send(self, message: str):
        if not self._token or not self._chat_id:
            logger.warning("Telegram not configured, skipping notification")
            return
        try:
            bot = await self._get_bot()
            await bot.send_message(chat_id=self._chat_id, text=message)
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")

    async def notify_trade(self, **kwargs):
        msg = format_trade_message(**kwargs)
        await self.send(msg)

    async def notify_daily_summary(self, **kwargs):
        msg = format_daily_summary(**kwargs)
        await self.send(msg)

    async def notify_circuit_breaker(self, **kwargs):
        msg = format_circuit_breaker(**kwargs)
        await self.send(msg)
