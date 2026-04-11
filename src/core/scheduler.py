import logging

from src.agents.technical import TechnicalAgent
from src.agents.fundamental import FundamentalAgent
from src.agents.sentiment import SentimentAgent
from src.agents.decision import DecisionAgent, should_invoke_decisor
from src.agents.risk import RiskAgent
from src.core.portfolio import PortfolioManager
from src.core.executor import Executor, OrderRequest
from src.config import get_settings

logger = logging.getLogger(__name__)


def _aggregate_should_trade(
    technical: float, fundamental: float, sentiment: float, threshold: int = 40
) -> bool:
    return should_invoke_decisor(technical, fundamental, sentiment, threshold)


class AnalysisCycle:
    def __init__(
        self,
        technical: TechnicalAgent,
        fundamental: FundamentalAgent,
        sentiment: SentimentAgent,
        decision: DecisionAgent,
        risk: RiskAgent,
        portfolio: PortfolioManager,
        executor: Executor,
    ):
        self.technical = technical
        self.fundamental = fundamental
        self.sentiment = sentiment
        self.decision = decision
        self.risk = risk
        self.portfolio = portfolio
        self.executor = executor

    async def run_for_symbol(self, symbol: str, bars_df) -> dict:
        """Run full analysis cycle for a single symbol."""
        settings = get_settings()
        result = {"symbol": symbol, "action": "HOLD", "reason": ""}

        # Step 1: Run technical analysis (sync, Python-pure)
        tech_result = self.technical.analyze(bars_df)
        logger.info(f"{symbol} technical_score={tech_result.score}")

        # Step 2: Run fundamental + sentiment in parallel
        fund_result = self.fundamental.analyze(symbol)
        sent_result = await self.sentiment.analyze(symbol)
        logger.info(f"{symbol} fundamental={fund_result.score} sentiment={sent_result.score}")

        # Step 3: Check if we should invoke the LLM decisor
        if not _aggregate_should_trade(
            tech_result.score, fund_result.score, sent_result.score,
            settings.min_signal_threshold,
        ):
            result["reason"] = "Signals below threshold"
            return result

        # Step 4: Get portfolio state and risk budget
        portfolio_state = self.portfolio.get_state()
        risk_budget = (settings.max_portfolio_heat - self.portfolio.get_portfolio_heat()) * 100

        if risk_budget <= 0:
            result["reason"] = "No risk budget available"
            return result

        # Step 5: Ask the decisor
        decision = await self.decision.decide(
            symbol=symbol,
            technical_score=tech_result.score,
            fundamental_score=fund_result.score,
            sentiment_score=sent_result.score,
            portfolio_state=portfolio_state,
            risk_budget_pct=min(risk_budget, settings.max_risk_per_trade * 100),
        )

        if decision.action == "HOLD" or decision.confidence < 0.6:
            result["action"] = "HOLD"
            result["reason"] = decision.reasoning
            return result

        # Step 6: Calculate position size
        current_price = tech_result.indicators.get("price", 0)
        if current_price == 0:
            result["reason"] = "No price data"
            return result

        stop_loss_price = current_price * (1 - decision.stop_loss_pct / 100)
        qty = self.risk.calculate_position_size(
            portfolio=portfolio_state,
            entry_price=current_price,
            stop_loss_price=stop_loss_price,
        )

        if qty == 0:
            result["reason"] = "Position size zero (circuit breaker or insufficient budget)"
            return result

        # Step 7: Pre-trade risk check
        risk_amount = qty * abs(current_price - stop_loss_price)
        order_info = {
            "symbol": symbol,
            "side": decision.action.lower(),
            "risk_amount": risk_amount,
            "sector": fund_result.indicators.get("sector", "Unknown"),
            "market_value": qty * current_price,
        }
        risk_check = self.risk.pre_trade_check(order_info, portfolio_state)

        if not risk_check.passed:
            result["reason"] = f"Risk check failed: {risk_check.failures}"
            logger.warning(f"{symbol} blocked by risk: {risk_check.failures}")
            return result

        # Step 8: Execute order
        order_req = OrderRequest(
            symbol=symbol,
            side=decision.action.lower(),
            qty=qty,
            entry_price=current_price,
            stop_loss_pct=decision.stop_loss_pct,
            take_profit_pct=decision.take_profit_pct,
            min_rr_ratio=settings.min_rr_ratio,
        )

        order_result = await self.executor.submit_bracket_order(order_req)
        result["action"] = decision.action
        result["reason"] = decision.reasoning
        result["order"] = order_result
        result["qty"] = qty
        result["confidence"] = decision.confidence

        return result
