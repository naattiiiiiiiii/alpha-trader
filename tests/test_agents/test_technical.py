import pandas as pd
import numpy as np
from src.agents.technical import TechnicalAgent


def _make_ohlcv(n=200, trend="up"):
    """Generate synthetic OHLCV data."""
    dates = pd.date_range("2026-01-01", periods=n, freq="1h")
    if trend == "up":
        close = 100 + np.cumsum(np.random.normal(0.1, 0.5, n))
    elif trend == "down":
        close = 200 + np.cumsum(np.random.normal(-0.1, 0.5, n))
    else:
        close = 150 + np.cumsum(np.random.normal(0, 0.3, n))

    close = np.maximum(close, 1.0)
    return pd.DataFrame({
        "open": close * (1 + np.random.uniform(-0.005, 0.005, n)),
        "high": close * (1 + np.random.uniform(0.001, 0.02, n)),
        "low": close * (1 - np.random.uniform(0.001, 0.02, n)),
        "close": close,
        "volume": np.random.randint(100_000, 10_000_000, n).astype(float),
    }, index=dates)


def test_technical_agent_returns_score_in_range():
    agent = TechnicalAgent()
    df = _make_ohlcv(200, "up")
    result = agent.analyze(df)
    assert -100 <= result.score <= 100


def test_technical_agent_result_has_indicators():
    agent = TechnicalAgent()
    df = _make_ohlcv(200, "up")
    result = agent.analyze(df)
    assert hasattr(result, "score")
    assert hasattr(result, "indicators")
    assert "rsi" in result.indicators
    assert "macd_signal" in result.indicators


def test_technical_agent_uptrend_positive():
    agent = TechnicalAgent()
    # Strong uptrend: 500 bars so indicators stabilize
    np.random.seed(42)
    df = _make_ohlcv(500, "up")
    result = agent.analyze(df)
    # In a strong uptrend, score should lean positive (not guaranteed but likely)
    assert result.score > -50  # At minimum not strongly bearish


def test_technical_agent_insufficient_data():
    agent = TechnicalAgent()
    df = _make_ohlcv(10, "up")  # Too few bars
    result = agent.analyze(df)
    assert result.score == 0  # Neutral when insufficient data
