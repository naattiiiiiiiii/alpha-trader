from dataclasses import dataclass
import logging

from src.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class OrderRequest:
    symbol: str
    side: str  # "buy" or "sell"
    qty: int
    entry_price: float
    stop_loss_pct: float
    take_profit_pct: float
    order_type: str = "market"  # "market" or "limit"
    min_rr_ratio: float = 0.0

    def __post_init__(self):
        if self.qty <= 0:
            raise ValueError("qty must be positive")
        if self.min_rr_ratio > 0 and self.take_profit_pct / self.stop_loss_pct < self.min_rr_ratio:
            raise ValueError(
                f"risk/reward ratio {self.take_profit_pct/self.stop_loss_pct:.1f} "
                f"below minimum {self.min_rr_ratio}"
            )

    @property
    def stop_loss_price(self) -> float:
        if self.side == "buy":
            return round(self.entry_price * (1 - self.stop_loss_pct / 100), 2)
        return round(self.entry_price * (1 + self.stop_loss_pct / 100), 2)

    @property
    def take_profit_price(self) -> float:
        if self.side == "buy":
            return round(self.entry_price * (1 + self.take_profit_pct / 100), 2)
        return round(self.entry_price * (1 - self.take_profit_pct / 100), 2)


class Executor:
    def __init__(self, api_key: str = "", secret_key: str = "", paper: bool = True):
        try:
            from alpaca.trading.client import TradingClient
            settings = get_settings()
            self._client = TradingClient(
                api_key=api_key or settings.alpaca_api_key,
                secret_key=secret_key or settings.alpaca_secret_key,
                paper=paper,
            )
        except Exception as e:
            logger.warning(f"Alpaca client init failed (OK for testing): {e}")
            self._client = None

    async def submit_bracket_order(self, req: OrderRequest) -> dict:
        """Submit a bracket order (entry + take-profit + stop-loss)."""
        try:
            from alpaca.trading.requests import MarketOrderRequest
            from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass

            order_data = MarketOrderRequest(
                symbol=req.symbol,
                qty=req.qty,
                side=OrderSide.BUY if req.side == "buy" else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
                order_class=OrderClass.BRACKET,
                take_profit={"limit_price": req.take_profit_price},
                stop_loss={"stop_price": req.stop_loss_price},
            )
            order = self._client.submit_order(order_data)
            logger.info(f"Order submitted: {req.side} {req.qty} {req.symbol} | "
                       f"TP={req.take_profit_price} SL={req.stop_loss_price}")
            return {"order_id": str(order.id), "status": order.status.value}
        except Exception as e:
            logger.error(f"Order failed: {e}")
            return {"order_id": None, "status": "error", "error": str(e)}

    async def close_position(self, symbol: str) -> dict:
        """Close an entire position."""
        try:
            self._client.close_position(symbol)
            logger.info(f"Position closed: {symbol}")
            return {"status": "closed", "symbol": symbol}
        except Exception as e:
            logger.error(f"Close position failed: {e}")
            return {"status": "error", "error": str(e)}

    async def close_all_positions(self) -> dict:
        """Close all open positions (circuit breaker)."""
        try:
            self._client.close_all_positions(cancel_orders=True)
            logger.info("All positions closed (circuit breaker)")
            return {"status": "all_closed"}
        except Exception as e:
            logger.error(f"Close all failed: {e}")
            return {"status": "error", "error": str(e)}

    def get_account(self) -> dict:
        """Get current account state."""
        account = self._client.get_account()
        return {
            "equity": float(account.equity),
            "cash": float(account.cash),
            "buying_power": float(account.buying_power),
            "portfolio_value": float(account.portfolio_value),
        }

    def get_positions(self) -> list[dict]:
        """Get all open positions."""
        positions = self._client.get_all_positions()
        return [
            {
                "symbol": p.symbol,
                "qty": float(p.qty),
                "side": p.side.value,
                "entry_price": float(p.avg_entry_price),
                "current_price": float(p.current_price),
                "market_value": float(p.market_value),
                "unrealized_pnl": float(p.unrealized_pl),
                "unrealized_pnl_pct": float(p.unrealized_plpc),
            }
            for p in positions
        ]
