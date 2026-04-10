from dataclasses import dataclass, field
import enum


class RiskLevel(enum.Enum):
    NORMAL = "normal"
    REDUCED_50 = "reduced_50"
    REDUCED_25 = "reduced_25"
    STOPPED = "stopped"


CIRCUIT_BREAKER_MULTIPLIER = {
    RiskLevel.NORMAL: 1.0,
    RiskLevel.REDUCED_50: 0.5,
    RiskLevel.REDUCED_25: 0.25,
    RiskLevel.STOPPED: 0.0,
}


@dataclass
class PreTradeCheck:
    passed: bool
    failures: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


class RiskAgent:
    def __init__(
        self,
        max_risk_per_trade: float = 0.02,
        max_daily_loss: float = 0.03,
        max_portfolio_heat: float = 0.06,
        max_drawdown: float = 0.10,
        max_sector_exposure: float = 0.25,
        max_consecutive_losses: int = 3,
        min_rr_ratio: float = 2.0,
    ):
        self.max_risk_per_trade = max_risk_per_trade
        self.max_daily_loss = max_daily_loss
        self.max_portfolio_heat = max_portfolio_heat
        self.max_drawdown = max_drawdown
        self.max_sector_exposure = max_sector_exposure
        self.max_consecutive_losses = max_consecutive_losses
        self.min_rr_ratio = min_rr_ratio

    def pre_trade_check(self, order: dict, portfolio: dict) -> PreTradeCheck:
        failures = []
        details = {}
        equity = portfolio["equity"]

        # Level 1: Per-trade risk
        risk_amount = order["risk_amount"]
        risk_pct = risk_amount / equity
        if risk_pct > self.max_risk_per_trade:
            failures.append("max_risk_per_trade")
            details["risk_pct"] = risk_pct

        # Level 2: Daily loss
        daily_loss_pct = abs(min(0, portfolio["daily_pnl"])) / equity
        if daily_loss_pct >= self.max_daily_loss:
            failures.append("max_daily_loss")
            details["daily_loss_pct"] = daily_loss_pct

        # Level 2: Consecutive losses
        if portfolio["consecutive_losses"] >= self.max_consecutive_losses:
            failures.append("max_consecutive_losses")
            details["consecutive_losses"] = portfolio["consecutive_losses"]

        # Level 3: Portfolio heat
        current_heat = sum(p["risk_amount"] for p in portfolio["positions"])
        new_heat = (current_heat + risk_amount) / equity
        if new_heat > self.max_portfolio_heat:
            failures.append("max_portfolio_heat")
            details["portfolio_heat"] = new_heat

        # Level 3: Sector exposure
        sector = order.get("sector")
        if sector:
            sector_value = sum(
                p.get("market_value", 0) for p in portfolio["positions"]
                if p.get("sector") == sector
            ) + order.get("market_value", 0)
            sector_pct = sector_value / equity
            if sector_pct > self.max_sector_exposure:
                failures.append("max_sector_exposure")
                details["sector_pct"] = sector_pct

        # Level 4: Circuit breaker
        cb_level = self.get_circuit_breaker_level(portfolio)
        if cb_level == RiskLevel.STOPPED:
            failures.append("circuit_breaker_stopped")

        return PreTradeCheck(
            passed=len(failures) == 0,
            failures=failures,
            details=details,
        )

    def get_circuit_breaker_level(self, portfolio: dict) -> RiskLevel:
        equity = portfolio["equity"]
        peak = portfolio["peak_equity"]
        drawdown = (peak - equity) / peak

        if drawdown >= self.max_drawdown:
            return RiskLevel.STOPPED
        elif drawdown >= 0.08:
            return RiskLevel.REDUCED_25
        elif drawdown >= 0.05:
            return RiskLevel.REDUCED_50
        return RiskLevel.NORMAL

    def calculate_position_size(
        self,
        portfolio: dict,
        entry_price: float,
        stop_loss_price: float,
    ) -> int:
        equity = portfolio["equity"]
        risk_budget = equity * self.max_risk_per_trade

        # Apply circuit breaker multiplier
        cb_level = self.get_circuit_breaker_level(portfolio)
        multiplier = CIRCUIT_BREAKER_MULTIPLIER[cb_level]
        risk_budget *= multiplier

        per_share_risk = abs(entry_price - stop_loss_price)
        if per_share_risk == 0:
            return 0

        qty = int(risk_budget / per_share_risk)
        return qty
