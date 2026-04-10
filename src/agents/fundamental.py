import yfinance as yf

from src.agents.base import BaseAgent, AgentResult


def _safe(val, default=None):
    """Return val if it's a valid number, else default."""
    if val is None:
        return default
    try:
        f = float(val)
        return default if f != f else f  # NaN check
    except (TypeError, ValueError):
        return default


def _compute_fundamental_score(metrics: dict) -> float:
    score = 0.0
    counted = 0

    pe = _safe(metrics.get("pe_ratio"))
    sector_pe = _safe(metrics.get("sector_pe_avg"))
    if pe is not None:
        counted += 1
        if pe < 0:
            score -= 10  # Negative earnings
        elif pe < 15:
            score += 15
        elif pe < 25:
            score += 5
        elif pe > 40:
            score -= 15
        if sector_pe and pe < sector_pe * 0.8:
            score += 5  # Undervalued vs sector

    peg = _safe(metrics.get("peg_ratio"))
    if peg is not None:
        counted += 1
        if 0 < peg < 1:
            score += 15  # Growth at discount
        elif peg < 1.5:
            score += 5
        elif peg > 3:
            score -= 10

    roe = _safe(metrics.get("roe"))
    if roe is not None:
        counted += 1
        if roe > 0.20:
            score += 15
        elif roe > 0.10:
            score += 5
        elif roe < 0:
            score -= 15

    net_margin = _safe(metrics.get("net_margin"))
    if net_margin is not None:
        counted += 1
        if net_margin > 0.20:
            score += 10
        elif net_margin > 0.10:
            score += 5
        elif net_margin < 0:
            score -= 10

    de = _safe(metrics.get("debt_to_equity"))
    if de is not None:
        counted += 1
        if de < 0.5:
            score += 10
        elif de < 1.0:
            score += 5
        elif de > 2.0:
            score -= 15

    cr = _safe(metrics.get("current_ratio"))
    if cr is not None:
        counted += 1
        if cr > 2.0:
            score += 10
        elif cr > 1.0:
            score += 5
        elif cr < 1.0:
            score -= 10

    fcf = _safe(metrics.get("free_cash_flow"))
    if fcf is not None:
        counted += 1
        if fcf > 0:
            score += 10
        else:
            score -= 10

    rev_growth = _safe(metrics.get("revenue_growth"))
    if rev_growth is not None:
        counted += 1
        if rev_growth > 0.20:
            score += 15
        elif rev_growth > 0.05:
            score += 5
        elif rev_growth < 0:
            score -= 10

    eps_growth = _safe(metrics.get("eps_growth"))
    if eps_growth is not None:
        counted += 1
        if eps_growth > 0.20:
            score += 10
        elif eps_growth > 0.05:
            score += 5
        elif eps_growth < 0:
            score -= 10

    if counted == 0:
        return 0

    return max(-100, min(100, score))


class FundamentalAgent(BaseAgent):
    name = "fundamental"

    def analyze(self, symbol: str) -> AgentResult:
        try:
            metrics = self._fetch_metrics(symbol)
        except Exception as e:
            return AgentResult(score=0, reasoning=f"Failed to fetch data: {e}")

        score = _compute_fundamental_score(metrics)
        return AgentResult(score=score, indicators=metrics)

    def _fetch_metrics(self, symbol: str) -> dict:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "peg_ratio": info.get("pegRatio"),
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            "net_margin": info.get("profitMargins"),
            "debt_to_equity": info.get("debtToEquity", 0) / 100 if info.get("debtToEquity") else None,
            "current_ratio": info.get("currentRatio"),
            "free_cash_flow": info.get("freeCashflow"),
            "revenue_growth": info.get("revenueGrowth"),
            "eps_growth": info.get("earningsGrowth"),
            "sector_pe_avg": info.get("industryPE"),
        }
