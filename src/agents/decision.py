import json
from dataclasses import dataclass
import anthropic


@dataclass
class DecisionOutput:
    action: str  # BUY, SELL, HOLD
    symbol: str
    position_size_pct: float
    entry_strategy: str  # market, limit
    take_profit_pct: float
    stop_loss_pct: float
    reasoning: str
    time_horizon: str  # day, swing, position
    confidence: float  # 0.0 to 1.0


def should_invoke_decisor(
    technical: float, fundamental: float, sentiment: float, threshold: int = 40
) -> bool:
    """Only invoke LLM when at least 2 of 3 agents give significant signal."""
    significant = sum(1 for s in [technical, fundamental, sentiment] if abs(s) >= threshold)
    return significant >= 2


def _build_decision_prompt(
    symbol: str,
    technical_score: float,
    fundamental_score: float,
    sentiment_score: float,
    portfolio_state: dict,
    risk_budget_pct: float,
) -> str:
    return f"""You are a professional portfolio manager. Analyze the following signals and make a trading decision.

Symbol: {symbol}

Agent Scores (-100 bearish to +100 bullish):
- Technical Analysis: {technical_score}
- Fundamental Analysis: {fundamental_score}
- Sentiment Analysis: {sentiment_score}

Portfolio State:
- Equity: ${portfolio_state.get('equity', 0):,.2f}
- Cash: ${portfolio_state.get('cash', 0):,.2f}
- Open positions: {len(portfolio_state.get('positions', []))}
- Available risk budget: {risk_budget_pct}% of portfolio

Rules:
- Never risk more than {risk_budget_pct}% of portfolio on this trade
- Stop-loss is MANDATORY for every trade
- Minimum risk/reward ratio: 2:1
- If signals are mixed or weak, HOLD is always valid
- Be conservative — only trade with high conviction

Respond with ONLY a JSON object:
{{"action": "BUY|SELL|HOLD", "symbol": "{symbol}", "position_size_pct": <float>, "entry_strategy": "market|limit", "take_profit_pct": <float>, "stop_loss_pct": <float>, "reasoning": "<brief explanation>", "time_horizon": "day|swing|position", "confidence": <0.0-1.0>}}"""


def _parse_decision(text: str) -> DecisionOutput:
    try:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(text)
        return DecisionOutput(
            action=data.get("action", "HOLD").upper(),
            symbol=data.get("symbol", ""),
            position_size_pct=float(data.get("position_size_pct", 0)),
            entry_strategy=data.get("entry_strategy", "limit"),
            take_profit_pct=float(data.get("take_profit_pct", 0)),
            stop_loss_pct=float(data.get("stop_loss_pct", 0)),
            reasoning=data.get("reasoning", ""),
            time_horizon=data.get("time_horizon", "swing"),
            confidence=float(data.get("confidence", 0)),
        )
    except (json.JSONDecodeError, ValueError, KeyError):
        return DecisionOutput(
            action="HOLD", symbol="", position_size_pct=0,
            entry_strategy="none", take_profit_pct=0, stop_loss_pct=0,
            reasoning="Failed to parse decision", time_horizon="none", confidence=0.0,
        )


class DecisionAgent:
    name = "decision"

    def __init__(self, api_key: str):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def decide(
        self,
        symbol: str,
        technical_score: float,
        fundamental_score: float,
        sentiment_score: float,
        portfolio_state: dict,
        risk_budget_pct: float,
    ) -> DecisionOutput:
        prompt = _build_decision_prompt(
            symbol=symbol,
            technical_score=technical_score,
            fundamental_score=fundamental_score,
            sentiment_score=sentiment_score,
            portfolio_state=portfolio_state,
            risk_budget_pct=risk_budget_pct,
        )
        try:
            response = await self._client.messages.create(
                model="claude-sonnet-4-6-20250514",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            return _parse_decision(response.content[0].text)
        except Exception as e:
            return DecisionOutput(
                action="HOLD", symbol=symbol, position_size_pct=0,
                entry_strategy="none", take_profit_pct=0, stop_loss_pct=0,
                reasoning=f"LLM error: {e}", time_horizon="none", confidence=0.0,
            )
