import threading


class PortfolioManager:
    def __init__(self, initial_equity: float = 100_000):
        self._equity = initial_equity
        self._cash = initial_equity
        self._buying_power = initial_equity
        self._peak_equity = initial_equity
        self._daily_pnl = 0.0
        self._consecutive_losses = 0
        self._positions: list[dict] = []
        self._lock = threading.Lock()

    def update_from_account(self, equity: float, cash: float, buying_power: float):
        with self._lock:
            self._equity = equity
            self._cash = cash
            self._buying_power = buying_power
            if equity > self._peak_equity:
                self._peak_equity = equity

    def update_positions(self, positions: list[dict]):
        with self._lock:
            self._positions = positions

    def record_trade_result(self, pnl: float):
        with self._lock:
            self._daily_pnl += pnl
            if pnl < 0:
                self._consecutive_losses += 1
            else:
                self._consecutive_losses = 0

    def reset_daily(self):
        with self._lock:
            self._daily_pnl = 0.0

    def get_drawdown_pct(self) -> float:
        if self._peak_equity == 0:
            return 0.0
        return (self._peak_equity - self._equity) / self._peak_equity

    def get_portfolio_heat(self) -> float:
        if self._equity == 0:
            return 0.0
        total_risk = sum(p.get("risk_amount", 0) for p in self._positions)
        return total_risk / self._equity

    def get_state(self) -> dict:
        with self._lock:
            return {
                "equity": self._equity,
                "cash": self._cash,
                "buying_power": self._buying_power,
                "peak_equity": self._peak_equity,
                "daily_pnl": self._daily_pnl,
                "consecutive_losses": self._consecutive_losses,
                "positions": list(self._positions),
                "drawdown_pct": self.get_drawdown_pct(),
                "portfolio_heat": self.get_portfolio_heat(),
            }
