# Alpha Trader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an autonomous stock trading agent with professional 5-level risk management, multi-agent analysis (technical + fundamental + sentiment + decision + risk), and a real-time dashboard — deployed to Railway cloud.

**Architecture:** Hybrid approach — Python-pure agents for technical/fundamental/risk analysis (fast, free, deterministic), Claude LLM only for sentiment analysis and strategic decisions. FastAPI + HTMX dashboard for monitoring. PostgreSQL for persistence. Telegram for notifications. All running 24/7 on Railway.

**Tech Stack:** Python 3.12+, uv, alpaca-py, FastAPI, Jinja2+HTMX, anthropic SDK, pandas-ta, yfinance, SQLAlchemy 2.0, Alembic, APScheduler 4.x, python-telegram-bot, pydantic-settings, Docker, Railway.

**Spec:** `docs/superpowers/specs/2026-04-10-alpha-trader-design.md`

---

## Task 1: Project Scaffolding and Config

**Files:**
- Create: `pyproject.toml`
- Create: `src/__init__.py`
- Create: `src/config.py`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Initialize project with uv**

```bash
cd ~/alpha-trader
uv init --lib --name alpha-trader
```

- [ ] **Step 2: Add dependencies to pyproject.toml**

Replace the generated `pyproject.toml` with:

```toml
[project]
name = "alpha-trader"
version = "0.1.0"
description = "Autonomous stock trading agent with professional risk management"
requires-python = ">=3.12"
dependencies = [
    "alpaca-py>=0.33.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "jinja2>=3.1.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "alembic>=1.14.0",
    "asyncpg>=0.30.0",
    "apscheduler>=4.0.0",
    "anthropic>=0.42.0",
    "pandas>=2.2.0",
    "pandas-ta>=0.3.14b1",
    "yfinance>=0.2.40",
    "python-telegram-bot>=21.0",
    "pydantic-settings>=2.7.0",
    "httpx>=0.28.0",
    "sse-starlette>=2.0.0",
    "python-multipart>=0.0.18",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.25.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.8.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 100
```

- [ ] **Step 3: Install dependencies**

```bash
cd ~/alpha-trader
uv sync --all-extras
```

- [ ] **Step 4: Create .gitignore**

```gitignore
__pycache__/
*.py[cod]
.env
.venv/
*.egg-info/
dist/
build/
.pytest_cache/
.ruff_cache/
*.db
```

- [ ] **Step 5: Create .env.example**

```env
# Alpaca
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_PAPER=true

# Claude API
ANTHROPIC_API_KEY=your_key_here

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/alpha_trader

# Telegram
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Risk params
MAX_RISK_PER_TRADE=0.02
MAX_DAILY_LOSS=0.03
MAX_PORTFOLIO_HEAT=0.06
MAX_DRAWDOWN=0.10
MAX_SECTOR_EXPOSURE=0.25
```

- [ ] **Step 6: Create src/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Alpaca
    alpaca_api_key: str
    alpaca_secret_key: str
    alpaca_paper: bool = True

    # Claude API
    anthropic_api_key: str

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/alpha_trader"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Risk parameters
    max_risk_per_trade: float = 0.02
    max_daily_loss: float = 0.03
    max_portfolio_heat: float = 0.06
    max_drawdown: float = 0.10
    max_sector_exposure: float = 0.25

    # Agent settings
    analysis_interval_minutes: int = 15
    max_watchlist_size: int = 50
    min_signal_threshold: int = 40
    min_rr_ratio: float = 2.0
    max_consecutive_losses: int = 3

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 7: Create tests/conftest.py**

```python
import pytest


@pytest.fixture
def risk_settings():
    """Default risk settings for testing."""
    return {
        "max_risk_per_trade": 0.02,
        "max_daily_loss": 0.03,
        "max_portfolio_heat": 0.06,
        "max_drawdown": 0.10,
        "max_sector_exposure": 0.25,
        "max_consecutive_losses": 3,
        "min_rr_ratio": 2.0,
    }


@pytest.fixture
def sample_portfolio():
    """Sample portfolio state for testing."""
    return {
        "equity": 100_000.0,
        "cash": 80_000.0,
        "buying_power": 80_000.0,
        "peak_equity": 100_000.0,
        "daily_pnl": 0.0,
        "positions": [],
        "consecutive_losses": 0,
    }
```

- [ ] **Step 8: Create src/__init__.py and tests/__init__.py**

Both files are empty:

```python
```

- [ ] **Step 9: Verify setup**

```bash
cd ~/alpha-trader
uv run python -c "from src.config import Settings; print('Config OK')"
uv run pytest --co  # collect tests, verify pytest works
```

- [ ] **Step 10: Commit**

```bash
cd ~/alpha-trader
git add pyproject.toml src/ tests/ .env.example .gitignore uv.lock
git commit -m "feat: project scaffolding with config and dependencies"
```

---

## Task 2: Database Models and Migrations

**Files:**
- Create: `src/models/__init__.py`
- Create: `src/models/database.py`
- Create: `src/models/trade.py`
- Create: `src/models/signal.py`
- Create: `src/models/risk_event.py`
- Create: `src/models/snapshot.py`
- Create: `src/models/config.py`
- Create: `tests/test_models/__init__.py`
- Create: `tests/test_models/test_trade.py`

- [ ] **Step 1: Write test for Trade model**

Create `tests/test_models/test_trade.py`:

```python
from src.models.trade import Trade
from sqlalchemy import inspect


def test_trade_table_name():
    assert Trade.__tablename__ == "trades"


def test_trade_columns():
    columns = {c.name for c in inspect(Trade).columns}
    expected = {
        "id", "symbol", "side", "qty", "entry_price", "exit_price",
        "entry_time", "exit_time", "status", "stop_loss", "take_profit",
        "pnl", "pnl_pct", "alpaca_order_id", "time_horizon",
    }
    assert expected.issubset(columns)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/alpha-trader
uv run pytest tests/test_models/test_trade.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.models.trade'`

- [ ] **Step 3: Create src/models/database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
```

- [ ] **Step 4: Create src/models/trade.py**

```python
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from src.models.database import Base


class TradeStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TradeSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class TimeHorizon(str, enum.Enum):
    DAY = "day"
    SWING = "swing"
    POSITION = "position"


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), index=True)
    side: Mapped[str] = mapped_column(SAEnum(TradeSide))
    qty: Mapped[float] = mapped_column(Float)
    entry_price: Mapped[float] = mapped_column(Float)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    entry_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(SAEnum(TradeStatus), default=TradeStatus.OPEN)
    stop_loss: Mapped[float] = mapped_column(Float)
    take_profit: Mapped[float] = mapped_column(Float)
    pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    pnl_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    alpaca_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    time_horizon: Mapped[str] = mapped_column(SAEnum(TimeHorizon), default=TimeHorizon.SWING)
```

- [ ] **Step 5: Create src/models/signal.py**

```python
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.database import Base


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    technical_score: Mapped[float] = mapped_column(Float)
    fundamental_score: Mapped[float] = mapped_column(Float)
    sentiment_score: Mapped[float] = mapped_column(Float)
    decision: Mapped[str] = mapped_column(String(10))  # BUY, SELL, HOLD
    confidence: Mapped[float] = mapped_column(Float)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
```

- [ ] **Step 6: Create src/models/risk_event.py**

```python
from datetime import datetime
from sqlalchemy import String, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.models.database import Base


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    event_type: Mapped[str] = mapped_column(String(50))
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    level: Mapped[str] = mapped_column(String(20))  # INFO, WARNING, CRITICAL
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
```

- [ ] **Step 7: Create src/models/snapshot.py**

```python
from datetime import datetime
from sqlalchemy import Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.models.database import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    equity: Mapped[float] = mapped_column(Float)
    cash: Mapped[float] = mapped_column(Float)
    buying_power: Mapped[float] = mapped_column(Float)
    total_pnl: Mapped[float] = mapped_column(Float)
    daily_pnl: Mapped[float] = mapped_column(Float)
    drawdown_pct: Mapped[float] = mapped_column(Float)
    positions_count: Mapped[int] = mapped_column(Integer)
    portfolio_heat: Mapped[float] = mapped_column(Float)
```

- [ ] **Step 8: Create src/models/config.py (agent_config table)**

```python
from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.models.database import Base


class AgentConfig(Base):
    __tablename__ = "agent_config"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

- [ ] **Step 9: Create src/models/__init__.py**

```python
from src.models.database import Base, engine, async_session, get_session
from src.models.trade import Trade, TradeStatus, TradeSide, TimeHorizon
from src.models.signal import Signal
from src.models.risk_event import RiskEvent
from src.models.snapshot import PortfolioSnapshot
from src.models.config import AgentConfig

__all__ = [
    "Base", "engine", "async_session", "get_session",
    "Trade", "TradeStatus", "TradeSide", "TimeHorizon",
    "Signal", "RiskEvent", "PortfolioSnapshot", "AgentConfig",
]
```

- [ ] **Step 10: Run test to verify it passes**

```bash
cd ~/alpha-trader
uv run pytest tests/test_models/test_trade.py -v
```

Expected: PASS

- [ ] **Step 11: Initialize Alembic**

```bash
cd ~/alpha-trader
uv run alembic init alembic
```

Edit `alembic/env.py` — replace the `target_metadata` line and add imports:

```python
# At the top, add:
from src.models.database import Base
from src.models import Trade, Signal, RiskEvent, PortfolioSnapshot, AgentConfig
from src.config import settings

# Replace target_metadata = None with:
target_metadata = Base.metadata

# In run_migrations_online(), replace the url config:
config.set_main_option("sqlalchemy.url", settings.database_url.replace("+asyncpg", ""))
```

- [ ] **Step 12: Commit**

```bash
cd ~/alpha-trader
git add src/models/ tests/test_models/ alembic/ alembic.ini
git commit -m "feat: database models for trades, signals, risk events, snapshots, config"
```

---

## Task 3: Agent Base Class and Technical Agent

**Files:**
- Create: `src/agents/__init__.py`
- Create: `src/agents/base.py`
- Create: `src/agents/technical.py`
- Create: `src/utils/__init__.py`
- Create: `src/utils/indicators.py`
- Create: `tests/test_agents/__init__.py`
- Create: `tests/test_agents/test_technical.py`

- [ ] **Step 1: Write tests for technical agent**

Create `tests/test_agents/test_technical.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_agents/test_technical.py -v
```

Expected: FAIL — module not found

- [ ] **Step 3: Create src/agents/base.py**

```python
from dataclasses import dataclass, field


@dataclass
class AgentResult:
    score: float  # -100 to +100
    indicators: dict = field(default_factory=dict)
    reasoning: str = ""


class BaseAgent:
    """Base class for all analysis agents."""

    name: str = "base"

    def analyze(self, *args, **kwargs) -> AgentResult:
        raise NotImplementedError
```

- [ ] **Step 4: Create src/agents/technical.py**

```python
import pandas as pd
import pandas_ta as ta

from src.agents.base import BaseAgent, AgentResult

MIN_BARS = 50


class TechnicalAgent(BaseAgent):
    name = "technical"

    def analyze(self, df: pd.DataFrame) -> AgentResult:
        if len(df) < MIN_BARS:
            return AgentResult(score=0, indicators={}, reasoning="Insufficient data")

        indicators = self._compute_indicators(df)
        score = self._compute_score(indicators)
        return AgentResult(score=score, indicators=indicators)

    def _compute_indicators(self, df: pd.DataFrame) -> dict:
        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        # Trend
        ema_9 = ta.ema(close, length=9).iloc[-1]
        ema_21 = ta.ema(close, length=21).iloc[-1]
        ema_50 = ta.ema(close, length=50).iloc[-1]
        macd_df = ta.macd(close)
        macd_val = macd_df.iloc[-1, 0]  # MACD line
        macd_signal = macd_df.iloc[-1, 1]  # Signal line
        macd_hist = macd_df.iloc[-1, 2]  # Histogram
        adx_df = ta.adx(high, low, close)
        adx_val = adx_df.iloc[-1, 0]  # ADX value

        # Momentum
        rsi = ta.rsi(close, length=14).iloc[-1]
        stoch_rsi = ta.stochrsi(close)
        stoch_k = stoch_rsi.iloc[-1, 0] if stoch_rsi is not None else 50.0
        willr = ta.willr(high, low, close).iloc[-1]

        # Volatility
        bbands = ta.bbands(close)
        bb_upper = bbands.iloc[-1, 0]
        bb_lower = bbands.iloc[-1, 2]
        atr = ta.atr(high, low, close, length=14).iloc[-1]

        # Volume
        obv = ta.obv(close, volume).iloc[-1]
        obv_prev = ta.obv(close, volume).iloc[-5]

        current_price = close.iloc[-1]

        return {
            "price": current_price,
            "ema_9": ema_9,
            "ema_21": ema_21,
            "ema_50": ema_50,
            "macd": macd_val,
            "macd_signal": macd_signal,
            "macd_hist": macd_hist,
            "adx": adx_val,
            "rsi": rsi,
            "stoch_k": stoch_k,
            "willr": willr,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "atr": atr,
            "obv": obv,
            "obv_trend": "up" if obv > obv_prev else "down",
        }

    def _compute_score(self, ind: dict) -> float:
        score = 0.0
        price = ind["price"]

        # Trend signals (weight: 35)
        if ind["ema_9"] > ind["ema_21"] > ind["ema_50"]:
            score += 20  # Strong uptrend alignment
        elif ind["ema_9"] < ind["ema_21"] < ind["ema_50"]:
            score -= 20  # Strong downtrend alignment

        if ind["macd_hist"] > 0:
            score += 10
        else:
            score -= 10

        if ind["adx"] > 25:  # Strong trend
            score += 5 if ind["ema_9"] > ind["ema_21"] else -5

        # Momentum signals (weight: 35)
        if ind["rsi"] < 30:
            score += 15  # Oversold — buy signal
        elif ind["rsi"] > 70:
            score -= 15  # Overbought — sell signal
        elif ind["rsi"] < 45:
            score += 5
        elif ind["rsi"] > 55:
            score -= 5

        if ind["stoch_k"] < 20:
            score += 10
        elif ind["stoch_k"] > 80:
            score -= 10

        if ind["willr"] < -80:
            score += 10  # Oversold
        elif ind["willr"] > -20:
            score -= 10  # Overbought

        # Volatility signals (weight: 15)
        if price < ind["bb_lower"]:
            score += 15  # Below lower band — potential bounce
        elif price > ind["bb_upper"]:
            score -= 15  # Above upper band — potential pullback

        # Volume signals (weight: 15)
        if ind["obv_trend"] == "up":
            score += 10 if score > 0 else 5  # Volume confirms direction
        else:
            score -= 10 if score < 0 else 5

        return max(-100, min(100, score))
```

- [ ] **Step 5: Create src/agents/__init__.py and src/utils/__init__.py**

Both empty:
```python
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_agents/test_technical.py -v
```

Expected: All 4 tests PASS

- [ ] **Step 7: Commit**

```bash
cd ~/alpha-trader
git add src/agents/ src/utils/ tests/test_agents/
git commit -m "feat: technical agent with trend, momentum, volatility, volume indicators"
```

---

## Task 4: Fundamental Agent

**Files:**
- Create: `src/agents/fundamental.py`
- Create: `tests/test_agents/test_fundamental.py`

- [ ] **Step 1: Write tests for fundamental agent**

Create `tests/test_agents/test_fundamental.py`:

```python
from src.agents.fundamental import FundamentalAgent, _compute_fundamental_score


def test_compute_score_strong_company():
    """A company with good fundamentals should score positive."""
    metrics = {
        "pe_ratio": 15.0,
        "pb_ratio": 2.0,
        "peg_ratio": 1.0,
        "roe": 0.20,
        "roa": 0.10,
        "net_margin": 0.15,
        "debt_to_equity": 0.5,
        "current_ratio": 2.0,
        "free_cash_flow": 5_000_000_000,
        "revenue_growth": 0.15,
        "eps_growth": 0.20,
        "sector_pe_avg": 20.0,
    }
    score = _compute_fundamental_score(metrics)
    assert score > 20  # Should be clearly positive


def test_compute_score_weak_company():
    """A company with poor fundamentals should score negative."""
    metrics = {
        "pe_ratio": 80.0,
        "pb_ratio": 10.0,
        "peg_ratio": 4.0,
        "roe": 0.02,
        "roa": 0.01,
        "net_margin": 0.01,
        "debt_to_equity": 3.0,
        "current_ratio": 0.5,
        "free_cash_flow": -1_000_000_000,
        "revenue_growth": -0.10,
        "eps_growth": -0.15,
        "sector_pe_avg": 20.0,
    }
    score = _compute_fundamental_score(metrics)
    assert score < -20  # Should be clearly negative


def test_compute_score_in_range():
    metrics = {
        "pe_ratio": 25.0,
        "pb_ratio": 3.0,
        "peg_ratio": 2.0,
        "roe": 0.10,
        "roa": 0.05,
        "net_margin": 0.08,
        "debt_to_equity": 1.0,
        "current_ratio": 1.5,
        "free_cash_flow": 1_000_000_000,
        "revenue_growth": 0.05,
        "eps_growth": 0.05,
        "sector_pe_avg": 22.0,
    }
    score = _compute_fundamental_score(metrics)
    assert -100 <= score <= 100


def test_compute_score_missing_data():
    """None values should not crash scoring."""
    metrics = {
        "pe_ratio": None,
        "pb_ratio": None,
        "peg_ratio": None,
        "roe": None,
        "roa": None,
        "net_margin": None,
        "debt_to_equity": None,
        "current_ratio": None,
        "free_cash_flow": None,
        "revenue_growth": None,
        "eps_growth": None,
        "sector_pe_avg": None,
    }
    score = _compute_fundamental_score(metrics)
    assert score == 0  # Neutral when no data
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_agents/test_fundamental.py -v
```

Expected: FAIL

- [ ] **Step 3: Create src/agents/fundamental.py**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_agents/test_fundamental.py -v
```

Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
cd ~/alpha-trader
git add src/agents/fundamental.py tests/test_agents/test_fundamental.py
git commit -m "feat: fundamental agent with valuation, profitability, health metrics"
```

---

## Task 5: Risk Agent

**Files:**
- Create: `src/agents/risk.py`
- Create: `tests/test_agents/test_risk.py`

- [ ] **Step 1: Write comprehensive risk agent tests**

Create `tests/test_agents/test_risk.py`:

```python
import pytest
from src.agents.risk import RiskAgent, PreTradeCheck, RiskLevel


@pytest.fixture
def agent(risk_settings):
    return RiskAgent(**risk_settings)


@pytest.fixture
def basic_portfolio(sample_portfolio):
    return sample_portfolio


def test_pre_trade_passes_valid_order(agent, basic_portfolio):
    order = {"symbol": "AAPL", "side": "buy", "risk_amount": 1500, "sector": "Technology"}
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is True
    assert len(result.failures) == 0


def test_pre_trade_blocks_excessive_risk(agent, basic_portfolio):
    order = {"symbol": "AAPL", "side": "buy", "risk_amount": 3000, "sector": "Technology"}
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is False
    assert "max_risk_per_trade" in result.failures


def test_pre_trade_blocks_daily_loss_exceeded(agent, basic_portfolio):
    basic_portfolio["daily_pnl"] = -2900  # Already lost 2.9% of 100K
    order = {"symbol": "AAPL", "side": "buy", "risk_amount": 500, "sector": "Technology"}
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is False
    assert "max_daily_loss" in result.failures


def test_pre_trade_blocks_portfolio_heat(agent, basic_portfolio):
    basic_portfolio["positions"] = [
        {"symbol": "TSLA", "risk_amount": 2000, "sector": "Consumer Cyclical"},
        {"symbol": "MSFT", "risk_amount": 2000, "sector": "Technology"},
        {"symbol": "GOOGL", "risk_amount": 1500, "sector": "Communication Services"},
    ]
    order = {"symbol": "AAPL", "side": "buy", "risk_amount": 1500, "sector": "Technology"}
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is False
    assert "max_portfolio_heat" in result.failures


def test_pre_trade_blocks_sector_overexposure(agent, basic_portfolio):
    basic_portfolio["positions"] = [
        {"symbol": "AAPL", "risk_amount": 1000, "sector": "Technology", "market_value": 20000},
        {"symbol": "MSFT", "risk_amount": 1000, "sector": "Technology", "market_value": 5000},
    ]
    order = {"symbol": "NVDA", "side": "buy", "risk_amount": 1000, "sector": "Technology", "market_value": 2000}
    # Total tech exposure would be 27K / 100K = 27% > 25%
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is False
    assert "max_sector_exposure" in result.failures


def test_pre_trade_blocks_consecutive_losses(agent, basic_portfolio):
    basic_portfolio["consecutive_losses"] = 3
    order = {"symbol": "AAPL", "side": "buy", "risk_amount": 500, "sector": "Technology"}
    result = agent.pre_trade_check(order, basic_portfolio)
    assert result.passed is False
    assert "max_consecutive_losses" in result.failures


def test_circuit_breaker_level_none(agent, basic_portfolio):
    level = agent.get_circuit_breaker_level(basic_portfolio)
    assert level == RiskLevel.NORMAL


def test_circuit_breaker_level_1(agent, basic_portfolio):
    basic_portfolio["equity"] = 95000  # 5% drawdown from 100K peak
    level = agent.get_circuit_breaker_level(basic_portfolio)
    assert level == RiskLevel.REDUCED_50


def test_circuit_breaker_level_2(agent, basic_portfolio):
    basic_portfolio["equity"] = 92000  # 8% drawdown
    level = agent.get_circuit_breaker_level(basic_portfolio)
    assert level == RiskLevel.REDUCED_25


def test_circuit_breaker_level_3(agent, basic_portfolio):
    basic_portfolio["equity"] = 89000  # 11% drawdown
    level = agent.get_circuit_breaker_level(basic_portfolio)
    assert level == RiskLevel.STOPPED


def test_position_size_calculation(agent, basic_portfolio):
    size = agent.calculate_position_size(
        portfolio=basic_portfolio,
        entry_price=100.0,
        stop_loss_price=96.0,
    )
    # Risk = 2% of 100K = $2000, per-share risk = $4, qty = 500
    assert size == 500


def test_position_size_respects_circuit_breaker(agent, basic_portfolio):
    basic_portfolio["equity"] = 95000  # Level 1: 50% reduction
    size = agent.calculate_position_size(
        portfolio=basic_portfolio,
        entry_price=100.0,
        stop_loss_price=96.0,
    )
    # Risk = 2% of 95K = $1900, 50% reduction = $950, per-share risk = $4, qty = 237
    assert size == 237
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_agents/test_risk.py -v
```

Expected: FAIL

- [ ] **Step 3: Create src/agents/risk.py**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_agents/test_risk.py -v
```

Expected: All 11 tests PASS

- [ ] **Step 5: Commit**

```bash
cd ~/alpha-trader
git add src/agents/risk.py tests/test_agents/test_risk.py
git commit -m "feat: risk agent with 5-level controls, circuit breakers, position sizing"
```

---

## Task 6: Sentiment Agent (Claude Haiku)

**Files:**
- Create: `src/agents/sentiment.py`
- Create: `tests/test_agents/test_sentiment.py`

- [ ] **Step 1: Write tests for sentiment agent**

Create `tests/test_agents/test_sentiment.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.sentiment import SentimentAgent, _build_prompt, _parse_response


def test_build_prompt():
    prompt = _build_prompt("AAPL", ["Apple beats Q1 earnings expectations"])
    assert "AAPL" in prompt
    assert "Apple beats" in prompt


def test_parse_response_valid():
    response = '{"score": 75, "summary": "Strong earnings beat", "urgency": "high"}'
    result = _parse_response(response)
    assert result["score"] == 75
    assert result["summary"] == "Strong earnings beat"


def test_parse_response_invalid_json():
    result = _parse_response("not json at all")
    assert result["score"] == 0
    assert "parse" in result["summary"].lower() or "error" in result["summary"].lower()


def test_parse_response_score_clamped():
    response = '{"score": 200, "summary": "test", "urgency": "low"}'
    result = _parse_response(response)
    assert result["score"] == 100  # Clamped to max


@pytest.mark.asyncio
async def test_sentiment_agent_uses_cache():
    agent = SentimentAgent(api_key="fake")
    agent._cache["AAPL"] = {
        "score": 50,
        "summary": "cached",
        "urgency": "low",
        "news_hash": "abc123",
    }
    # Same news hash should return cached result
    with patch.object(agent, "_fetch_news", return_value=[]):
        with patch.object(agent, "_compute_news_hash", return_value="abc123"):
            result = await agent.analyze("AAPL")
    assert result.score == 50
    assert "cached" in result.reasoning
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_agents/test_sentiment.py -v
```

Expected: FAIL

- [ ] **Step 3: Create src/agents/sentiment.py**

```python
import json
import hashlib
import anthropic

from src.agents.base import BaseAgent, AgentResult


def _build_prompt(symbol: str, news_items: list[str]) -> str:
    news_text = "\n".join(f"- {item}" for item in news_items) if news_items else "No recent news."
    return f"""Analyze the following news/events for stock {symbol} and assess their likely impact on the stock price in the short term (1-5 days).

Recent news:
{news_text}

Respond with ONLY a JSON object (no markdown, no explanation):
{{"score": <integer -100 to 100>, "summary": "<one line summary>", "urgency": "<low|medium|high>"}}

Score guide:
- +80 to +100: Extremely positive (major beat, FDA approval, huge contract)
- +40 to +79: Positive (good earnings, upgrade, positive guidance)
- -39 to +39: Neutral or mixed
- -79 to -40: Negative (miss, downgrade, lawsuit)
- -100 to -80: Extremely negative (fraud, bankruptcy risk, major recall)"""


def _parse_response(text: str) -> dict:
    try:
        # Try to extract JSON from response
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(text)
        score = max(-100, min(100, int(data.get("score", 0))))
        return {
            "score": score,
            "summary": data.get("summary", ""),
            "urgency": data.get("urgency", "low"),
        }
    except (json.JSONDecodeError, ValueError, KeyError):
        return {"score": 0, "summary": "Failed to parse LLM response", "urgency": "low"}


class SentimentAgent(BaseAgent):
    name = "sentiment"

    def __init__(self, api_key: str):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._cache: dict[str, dict] = {}

    def _compute_news_hash(self, news_items: list[str]) -> str:
        content = "|".join(sorted(news_items))
        return hashlib.md5(content.encode()).hexdigest()

    async def _fetch_news(self, symbol: str) -> list[str]:
        """Fetch news from Alpaca. Override in subclass or mock for testing."""
        # Will be connected to Alpaca news API in integration
        return []

    async def analyze(self, symbol: str) -> AgentResult:
        news_items = await self._fetch_news(symbol)
        news_hash = self._compute_news_hash(news_items)

        # Check cache
        cached = self._cache.get(symbol)
        if cached and cached.get("news_hash") == news_hash:
            return AgentResult(
                score=cached["score"],
                indicators={"cached": True, "urgency": cached.get("urgency", "low")},
                reasoning=f"cached: {cached['summary']}",
            )

        if not news_items:
            return AgentResult(score=0, reasoning="No news available")

        prompt = _build_prompt(symbol, news_items)
        try:
            response = await self._client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            parsed = _parse_response(response.content[0].text)
        except Exception as e:
            return AgentResult(score=0, reasoning=f"LLM error: {e}")

        # Update cache
        self._cache[symbol] = {**parsed, "news_hash": news_hash}

        return AgentResult(
            score=parsed["score"],
            indicators={"urgency": parsed["urgency"], "cached": False},
            reasoning=parsed["summary"],
        )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_agents/test_sentiment.py -v
```

Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
cd ~/alpha-trader
git add src/agents/sentiment.py tests/test_agents/test_sentiment.py
git commit -m "feat: sentiment agent with Claude Haiku, caching, news parsing"
```

---

## Task 7: Decision Agent (Claude Sonnet)

**Files:**
- Create: `src/agents/decision.py`
- Create: `tests/test_agents/test_decision.py`

- [ ] **Step 1: Write tests for decision agent**

Create `tests/test_agents/test_decision.py`:

```python
import pytest
from src.agents.decision import _build_decision_prompt, _parse_decision, DecisionOutput


def test_build_prompt_includes_all_scores():
    prompt = _build_decision_prompt(
        symbol="AAPL",
        technical_score=72,
        fundamental_score=45,
        sentiment_score=85,
        portfolio_state={"equity": 100000, "positions": [], "cash": 80000},
        risk_budget_pct=1.8,
    )
    assert "AAPL" in prompt
    assert "72" in prompt
    assert "45" in prompt
    assert "85" in prompt
    assert "1.8" in prompt


def test_parse_decision_valid():
    response = '''{
        "action": "BUY",
        "symbol": "AAPL",
        "position_size_pct": 1.5,
        "entry_strategy": "limit",
        "take_profit_pct": 4.0,
        "stop_loss_pct": 2.0,
        "reasoning": "Strong confluence",
        "time_horizon": "swing",
        "confidence": 0.82
    }'''
    result = _parse_decision(response)
    assert result.action == "BUY"
    assert result.symbol == "AAPL"
    assert result.confidence == 0.82
    assert result.stop_loss_pct == 2.0


def test_parse_decision_hold():
    response = '''{
        "action": "HOLD",
        "symbol": "AAPL",
        "position_size_pct": 0,
        "entry_strategy": "none",
        "take_profit_pct": 0,
        "stop_loss_pct": 0,
        "reasoning": "Mixed signals",
        "time_horizon": "none",
        "confidence": 0.3
    }'''
    result = _parse_decision(response)
    assert result.action == "HOLD"


def test_parse_decision_invalid_json():
    result = _parse_decision("garbage")
    assert result.action == "HOLD"
    assert result.confidence == 0.0


def test_should_invoke_decisor_true():
    from src.agents.decision import should_invoke_decisor
    assert should_invoke_decisor(technical=65, fundamental=50, sentiment=10, threshold=40) is True


def test_should_invoke_decisor_false():
    from src.agents.decision import should_invoke_decisor
    assert should_invoke_decisor(technical=10, fundamental=20, sentiment=10, threshold=40) is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_agents/test_decision.py -v
```

Expected: FAIL

- [ ] **Step 3: Create src/agents/decision.py**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_agents/test_decision.py -v
```

Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
cd ~/alpha-trader
git add src/agents/decision.py tests/test_agents/test_decision.py
git commit -m "feat: decision agent with Claude Sonnet, structured output, invocation guard"
```

---

## Task 8: Portfolio State Manager

**Files:**
- Create: `src/core/__init__.py`
- Create: `src/core/portfolio.py`
- Create: `tests/test_core/__init__.py`
- Create: `tests/test_core/test_portfolio.py`

- [ ] **Step 1: Write tests for portfolio manager**

Create `tests/test_core/test_portfolio.py`:

```python
from src.core.portfolio import PortfolioManager


def test_initial_state():
    pm = PortfolioManager(initial_equity=100_000)
    state = pm.get_state()
    assert state["equity"] == 100_000
    assert state["peak_equity"] == 100_000
    assert state["daily_pnl"] == 0
    assert state["consecutive_losses"] == 0
    assert len(state["positions"]) == 0


def test_update_from_alpaca():
    pm = PortfolioManager(initial_equity=100_000)
    pm.update_from_account(equity=102_000, cash=70_000, buying_power=70_000)
    state = pm.get_state()
    assert state["equity"] == 102_000
    assert state["peak_equity"] == 102_000  # New peak


def test_peak_tracks_highest():
    pm = PortfolioManager(initial_equity=100_000)
    pm.update_from_account(equity=105_000, cash=70_000, buying_power=70_000)
    pm.update_from_account(equity=103_000, cash=72_000, buying_power=72_000)
    state = pm.get_state()
    assert state["peak_equity"] == 105_000  # Still the old peak


def test_drawdown_calculation():
    pm = PortfolioManager(initial_equity=100_000)
    pm.update_from_account(equity=105_000, cash=70_000, buying_power=70_000)
    pm.update_from_account(equity=94_500, cash=80_000, buying_power=80_000)
    assert pm.get_drawdown_pct() == pytest.approx(0.10, abs=0.001)


def test_portfolio_heat():
    pm = PortfolioManager(initial_equity=100_000)
    pm.update_positions([
        {"symbol": "AAPL", "risk_amount": 1500, "sector": "Technology", "market_value": 10000},
        {"symbol": "TSLA", "risk_amount": 1000, "sector": "Consumer Cyclical", "market_value": 8000},
    ])
    assert pm.get_portfolio_heat() == pytest.approx(0.025, abs=0.001)


def test_record_trade_result_win():
    pm = PortfolioManager(initial_equity=100_000)
    pm.record_trade_result(pnl=500)
    assert pm._consecutive_losses == 0
    assert pm._daily_pnl == 500


def test_record_trade_result_loss():
    pm = PortfolioManager(initial_equity=100_000)
    pm.record_trade_result(pnl=-200)
    pm.record_trade_result(pnl=-300)
    assert pm._consecutive_losses == 2
    assert pm._daily_pnl == -500


def test_reset_daily():
    pm = PortfolioManager(initial_equity=100_000)
    pm.record_trade_result(pnl=-500)
    pm.reset_daily()
    assert pm._daily_pnl == 0
    # Consecutive losses persist across days
    assert pm._consecutive_losses == 1


import pytest
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_core/test_portfolio.py -v
```

Expected: FAIL

- [ ] **Step 3: Create src/core/portfolio.py**

```python
from dataclasses import dataclass, field
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
```

- [ ] **Step 4: Create src/core/__init__.py and tests/test_core/__init__.py**

Both empty.

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_core/test_portfolio.py -v
```

Expected: All 8 tests PASS

- [ ] **Step 6: Commit**

```bash
cd ~/alpha-trader
git add src/core/ tests/test_core/
git commit -m "feat: portfolio state manager with drawdown, heat, daily tracking"
```

---

## Task 9: Execution Engine (Alpaca Orders)

**Files:**
- Create: `src/core/executor.py`
- Create: `tests/test_core/test_executor.py`

- [ ] **Step 1: Write tests for executor**

Create `tests/test_core/test_executor.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.executor import Executor, OrderRequest


def test_order_request_bracket_prices():
    req = OrderRequest(
        symbol="AAPL",
        side="buy",
        qty=10,
        entry_price=100.0,
        stop_loss_pct=2.0,
        take_profit_pct=4.0,
    )
    assert req.stop_loss_price == 98.0
    assert req.take_profit_price == 104.0


def test_order_request_sell_bracket_prices():
    req = OrderRequest(
        symbol="AAPL",
        side="sell",
        qty=10,
        entry_price=100.0,
        stop_loss_pct=2.0,
        take_profit_pct=4.0,
    )
    # For short: stop is above, take profit is below
    assert req.stop_loss_price == 102.0
    assert req.take_profit_price == 96.0


def test_order_request_validates_qty():
    with pytest.raises(ValueError, match="qty must be positive"):
        OrderRequest(symbol="AAPL", side="buy", qty=0, entry_price=100.0,
                     stop_loss_pct=2.0, take_profit_pct=4.0)


def test_order_request_validates_rr_ratio():
    with pytest.raises(ValueError, match="risk/reward"):
        OrderRequest(symbol="AAPL", side="buy", qty=10, entry_price=100.0,
                     stop_loss_pct=5.0, take_profit_pct=2.0, min_rr_ratio=2.0)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_core/test_executor.py -v
```

Expected: FAIL

- [ ] **Step 3: Create src/core/executor.py**

```python
from dataclasses import dataclass
import logging
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest, LimitOrderRequest,
)
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass

from src.config import settings

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
        self._client = TradingClient(
            api_key=api_key or settings.alpaca_api_key,
            secret_key=secret_key or settings.alpaca_secret_key,
            paper=paper,
        )

    async def submit_bracket_order(self, req: OrderRequest) -> dict:
        """Submit a bracket order (entry + take-profit + stop-loss)."""
        try:
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_core/test_executor.py -v
```

Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
cd ~/alpha-trader
git add src/core/executor.py tests/test_core/test_executor.py
git commit -m "feat: execution engine with bracket orders, position management, account sync"
```

---

## Task 10: Scheduler and Main Orchestrator

**Files:**
- Create: `src/core/scheduler.py`
- Create: `src/main.py`
- Create: `tests/test_core/test_scheduler.py`

- [ ] **Step 1: Write tests for scheduler logic**

Create `tests/test_core/test_scheduler.py`:

```python
from src.core.scheduler import AnalysisCycle, _aggregate_should_trade


def test_aggregate_should_trade_strong_signals():
    result = _aggregate_should_trade(
        technical=72, fundamental=45, sentiment=85, threshold=40
    )
    assert result is True  # 3/3 above threshold


def test_aggregate_should_trade_two_signals():
    result = _aggregate_should_trade(
        technical=65, fundamental=50, sentiment=10, threshold=40
    )
    assert result is True  # 2/3 above threshold


def test_aggregate_should_trade_weak_signals():
    result = _aggregate_should_trade(
        technical=20, fundamental=15, sentiment=10, threshold=40
    )
    assert result is False  # 0/3 above threshold


def test_aggregate_should_trade_one_signal():
    result = _aggregate_should_trade(
        technical=80, fundamental=10, sentiment=5, threshold=40
    )
    assert result is False  # Only 1/3 above threshold
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_core/test_scheduler.py -v
```

Expected: FAIL

- [ ] **Step 3: Create src/core/scheduler.py**

```python
import asyncio
import logging
from datetime import datetime

from src.agents.technical import TechnicalAgent
from src.agents.fundamental import FundamentalAgent
from src.agents.sentiment import SentimentAgent
from src.agents.decision import DecisionAgent, should_invoke_decisor
from src.agents.risk import RiskAgent, RiskLevel
from src.core.portfolio import PortfolioManager
from src.core.executor import Executor, OrderRequest
from src.config import settings

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
```

- [ ] **Step 4: Create src/main.py (entry point)**

```python
import asyncio
import logging
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.config import settings
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
    logger.info("Alpha Trader starting...")

    # Initialize components
    technical = TechnicalAgent()
    fundamental = FundamentalAgent()
    sentiment = SentimentAgent(api_key=settings.anthropic_api_key)
    decision = DecisionAgent(api_key=settings.anthropic_api_key)
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
    logger.info("Alpha Trader stopped.")


async def run_analysis_cycle(cycle, watchlist, executor, portfolio):
    """Run one full analysis cycle across all watchlist symbols."""
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
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_core/test_scheduler.py -v
```

Expected: All 4 tests PASS

- [ ] **Step 6: Commit**

```bash
cd ~/alpha-trader
git add src/core/scheduler.py src/main.py tests/test_core/test_scheduler.py
git commit -m "feat: scheduler orchestrator and main entry point with analysis cycle"
```

---

## Task 11: Telegram Notifications

**Files:**
- Create: `src/notifications/__init__.py`
- Create: `src/notifications/telegram.py`
- Create: `tests/test_notifications/__init__.py`
- Create: `tests/test_notifications/test_telegram.py`

- [ ] **Step 1: Write tests for telegram formatter**

Create `tests/test_notifications/test_telegram.py`:

```python
from src.notifications.telegram import format_trade_message, format_daily_summary


def test_format_trade_buy():
    msg = format_trade_message(
        action="BUY", symbol="AAPL", qty=10, price=178.50,
        stop_loss=174.90, take_profit=185.20, reasoning="Strong confluence"
    )
    assert "BUY" in msg
    assert "AAPL" in msg
    assert "178.50" in msg
    assert "Strong confluence" in msg


def test_format_trade_stop_loss():
    msg = format_trade_message(
        action="STOP-LOSS", symbol="AAPL", qty=10, price=174.90,
        pnl=-36.0, pnl_pct=-2.0
    )
    assert "STOP-LOSS" in msg
    assert "-$36.00" in msg or "-36.00" in msg


def test_format_daily_summary():
    msg = format_daily_summary(
        trades_count=3, wins=2, losses=1,
        daily_pnl=85.30, equity=100_085.30,
        drawdown_pct=0.0,
    )
    assert "3" in msg
    assert "2" in msg
    assert "85.30" in msg
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_notifications/test_telegram.py -v
```

Expected: FAIL

- [ ] **Step 3: Create src/notifications/telegram.py**

```python
import logging
from telegram import Bot

from src.config import settings

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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_notifications/test_telegram.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
cd ~/alpha-trader
git add src/notifications/ tests/test_notifications/
git commit -m "feat: telegram notifications with trade, summary, circuit breaker messages"
```

---

## Task 12: Dashboard — FastAPI + HTMX (Overview + Positions)

**Files:**
- Create: `src/api/__init__.py`
- Create: `src/api/app.py`
- Create: `src/api/routes/__init__.py`
- Create: `src/api/routes/dashboard.py`
- Create: `src/api/routes/positions.py`
- Create: `src/api/templates/base.html`
- Create: `src/api/templates/overview.html`
- Create: `src/api/templates/positions.html`
- Create: `src/api/static/style.css`
- Create: `tests/test_api/__init__.py`
- Create: `tests/test_api/test_dashboard.py`

- [ ] **Step 1: Write tests for dashboard endpoints**

Create `tests/test_api/test_dashboard.py`:

```python
import pytest
from httpx import AsyncClient, ASGITransport
from src.api.app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.mark.asyncio
async def test_health_endpoint(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


@pytest.mark.asyncio
async def test_overview_page(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "Alpha Trader" in response.text
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_api/test_dashboard.py -v
```

Expected: FAIL

- [ ] **Step 3: Create src/api/app.py**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.positions import router as positions_router


def create_app() -> FastAPI:
    app = FastAPI(title="Alpha Trader", version="0.1.0")

    # Static files and templates
    static_dir = Path(__file__).parent / "static"
    templates_dir = Path(__file__).parent / "templates"
    static_dir.mkdir(exist_ok=True)
    templates_dir.mkdir(exist_ok=True)

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Health endpoint
    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "alpha-trader"}

    # Routes
    app.include_router(dashboard_router)
    app.include_router(positions_router)

    return app
```

- [ ] **Step 4: Create src/api/routes/dashboard.py**

```python
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/")
async def overview(request: Request):
    # TODO: Wire to real portfolio data in integration task
    context = {
        "request": request,
        "status": "ACTIVE",
        "equity": 100_000.00,
        "daily_pnl": 0.00,
        "total_pnl": 0.00,
        "drawdown_pct": 0.0,
        "positions_count": 0,
        "portfolio_heat": 0.0,
    }
    return templates.TemplateResponse("overview.html", context)
```

- [ ] **Step 5: Create src/api/routes/positions.py**

```python
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/positions")
async def positions_page(request: Request):
    context = {
        "request": request,
        "positions": [],
    }
    return templates.TemplateResponse("positions.html", context)
```

- [ ] **Step 6: Create src/api/templates/base.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alpha Trader</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
    <script src="https://unpkg.com/htmx-ext-sse@2.3.0/sse.js"></script>
</head>
<body>
    <nav>
        <div class="nav-brand">Alpha Trader</div>
        <div class="nav-links">
            <a href="/">Overview</a>
            <a href="/positions">Positions</a>
            <a href="/history">History</a>
            <a href="/signals">Signals</a>
            <a href="/settings">Settings</a>
            <a href="/logs">Logs</a>
        </div>
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

- [ ] **Step 7: Create src/api/templates/overview.html**

```html
{% extends "base.html" %}
{% block content %}
<h1>Dashboard</h1>
<div class="status-bar">
    <span class="status {{ 'active' if status == 'ACTIVE' else 'paused' }}">{{ status }}</span>
</div>
<div class="metrics-grid">
    <div class="metric-card">
        <div class="metric-label">Equity</div>
        <div class="metric-value">${{ "{:,.2f}".format(equity) }}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Daily P&L</div>
        <div class="metric-value {{ 'positive' if daily_pnl >= 0 else 'negative' }}">${{ "{:+,.2f}".format(daily_pnl) }}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Total P&L</div>
        <div class="metric-value {{ 'positive' if total_pnl >= 0 else 'negative' }}">${{ "{:+,.2f}".format(total_pnl) }}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Drawdown</div>
        <div class="metric-value">{{ "{:.1f}".format(drawdown_pct) }}%</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Positions</div>
        <div class="metric-value">{{ positions_count }}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Portfolio Heat</div>
        <div class="metric-value">{{ "{:.1f}".format(portfolio_heat * 100) }}%</div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 8: Create src/api/templates/positions.html**

```html
{% extends "base.html" %}
{% block content %}
<h1>Positions</h1>
{% if positions %}
<table>
    <thead>
        <tr>
            <th>Symbol</th>
            <th>Side</th>
            <th>Qty</th>
            <th>Entry</th>
            <th>Current</th>
            <th>P&L</th>
            <th>P&L %</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for p in positions %}
        <tr>
            <td>{{ p.symbol }}</td>
            <td>{{ p.side }}</td>
            <td>{{ p.qty }}</td>
            <td>${{ "{:.2f}".format(p.entry_price) }}</td>
            <td>${{ "{:.2f}".format(p.current_price) }}</td>
            <td class="{{ 'positive' if p.unrealized_pnl >= 0 else 'negative' }}">${{ "{:+.2f}".format(p.unrealized_pnl) }}</td>
            <td class="{{ 'positive' if p.unrealized_pnl_pct >= 0 else 'negative' }}">{{ "{:+.1f}".format(p.unrealized_pnl_pct * 100) }}%</td>
            <td>
                <button hx-post="/api/close/{{ p.symbol }}" hx-confirm="Close {{ p.symbol }}?">Close</button>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% else %}
<p class="empty-state">No open positions</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 9: Create src/api/static/style.css**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0f1117;
    color: #e1e4e8;
    line-height: 1.6;
}

nav {
    background: #161b22;
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    gap: 2rem;
    border-bottom: 1px solid #30363d;
}

.nav-brand { font-size: 1.3rem; font-weight: 700; color: #58a6ff; }
.nav-links { display: flex; gap: 1.5rem; }
.nav-links a { color: #8b949e; text-decoration: none; }
.nav-links a:hover { color: #e1e4e8; }

main { padding: 2rem; max-width: 1200px; margin: 0 auto; }

h1 { margin-bottom: 1.5rem; }

.status-bar { margin-bottom: 1.5rem; }
.status {
    padding: 0.3rem 1rem; border-radius: 4px;
    font-weight: 600; font-size: 0.85rem; text-transform: uppercase;
}
.status.active { background: #1a3a2a; color: #3fb950; }
.status.paused { background: #3d2a1a; color: #d29922; }

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 1.2rem;
}

.metric-label { font-size: 0.8rem; color: #8b949e; margin-bottom: 0.3rem; }
.metric-value { font-size: 1.5rem; font-weight: 700; }

.positive { color: #3fb950; }
.negative { color: #f85149; }

table {
    width: 100%;
    border-collapse: collapse;
    background: #161b22;
    border-radius: 8px;
    overflow: hidden;
}

th, td { padding: 0.8rem 1rem; text-align: left; border-bottom: 1px solid #30363d; }
th { background: #1c2128; color: #8b949e; font-size: 0.85rem; text-transform: uppercase; }

button {
    background: #21262d;
    color: #e1e4e8;
    border: 1px solid #30363d;
    padding: 0.3rem 0.8rem;
    border-radius: 4px;
    cursor: pointer;
}
button:hover { background: #30363d; }

.empty-state { color: #8b949e; text-align: center; padding: 3rem; }
```

- [ ] **Step 10: Create empty __init__.py files**

Create `src/api/__init__.py`, `src/api/routes/__init__.py`, `tests/test_api/__init__.py` — all empty.

- [ ] **Step 11: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_api/test_dashboard.py -v
```

Expected: All 2 tests PASS

- [ ] **Step 12: Commit**

```bash
cd ~/alpha-trader
git add src/api/ tests/test_api/
git commit -m "feat: dashboard with FastAPI + HTMX, overview and positions pages"
```

---

## Task 13: Dashboard — History, Signals, Settings, Logs Pages

**Files:**
- Create: `src/api/routes/history.py`
- Create: `src/api/routes/signals.py`
- Create: `src/api/routes/settings.py`
- Create: `src/api/routes/logs.py`
- Create: `src/api/templates/history.html`
- Create: `src/api/templates/signals.html`
- Create: `src/api/templates/settings.html`
- Create: `src/api/templates/logs.html`
- Modify: `src/api/app.py` (add new routers)

- [ ] **Step 1: Create src/api/routes/history.py**

```python
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/history")
async def history_page(request: Request):
    context = {
        "request": request,
        "trades": [],
        "stats": {"win_rate": 0, "avg_win": 0, "avg_loss": 0, "profit_factor": 0, "total_trades": 0},
    }
    return templates.TemplateResponse("history.html", context)
```

- [ ] **Step 2: Create src/api/routes/signals.py**

```python
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/signals")
async def signals_page(request: Request):
    context = {
        "request": request,
        "signals": [],
    }
    return templates.TemplateResponse("signals.html", context)
```

- [ ] **Step 3: Create src/api/routes/settings.py**

```python
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pathlib import Path

from src.config import settings

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/settings")
async def settings_page(request: Request):
    context = {
        "request": request,
        "settings": {
            "max_risk_per_trade": settings.max_risk_per_trade * 100,
            "max_daily_loss": settings.max_daily_loss * 100,
            "max_portfolio_heat": settings.max_portfolio_heat * 100,
            "max_drawdown": settings.max_drawdown * 100,
            "max_sector_exposure": settings.max_sector_exposure * 100,
            "analysis_interval": settings.analysis_interval_minutes,
            "max_watchlist_size": settings.max_watchlist_size,
        },
        "agent_status": "ACTIVE",
    }
    return templates.TemplateResponse("settings.html", context)
```

- [ ] **Step 4: Create src/api/routes/logs.py**

```python
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/logs")
async def logs_page(request: Request):
    context = {
        "request": request,
        "logs": [],
    }
    return templates.TemplateResponse("logs.html", context)
```

- [ ] **Step 5: Create templates — history.html**

```html
{% extends "base.html" %}
{% block content %}
<h1>Trade History</h1>
<div class="metrics-grid">
    <div class="metric-card">
        <div class="metric-label">Total Trades</div>
        <div class="metric-value">{{ stats.total_trades }}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Win Rate</div>
        <div class="metric-value">{{ "{:.0f}".format(stats.win_rate) }}%</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Avg Win</div>
        <div class="metric-value positive">${{ "{:.2f}".format(stats.avg_win) }}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Avg Loss</div>
        <div class="metric-value negative">${{ "{:.2f}".format(stats.avg_loss) }}</div>
    </div>
</div>
{% if trades %}
<table>
    <thead>
        <tr><th>Date</th><th>Symbol</th><th>Side</th><th>Qty</th><th>Entry</th><th>Exit</th><th>P&L</th><th>P&L %</th></tr>
    </thead>
    <tbody>
        {% for t in trades %}
        <tr>
            <td>{{ t.exit_time.strftime('%Y-%m-%d %H:%M') if t.exit_time else '-' }}</td>
            <td>{{ t.symbol }}</td>
            <td>{{ t.side }}</td>
            <td>{{ t.qty }}</td>
            <td>${{ "{:.2f}".format(t.entry_price) }}</td>
            <td>${{ "{:.2f}".format(t.exit_price) if t.exit_price else '-' }}</td>
            <td class="{{ 'positive' if (t.pnl or 0) >= 0 else 'negative' }}">${{ "{:+.2f}".format(t.pnl or 0) }}</td>
            <td class="{{ 'positive' if (t.pnl_pct or 0) >= 0 else 'negative' }}">{{ "{:+.1f}".format((t.pnl_pct or 0) * 100) }}%</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% else %}
<p class="empty-state">No completed trades yet</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 6: Create templates — signals.html**

```html
{% extends "base.html" %}
{% block content %}
<h1>Signals</h1>
{% if signals %}
<table>
    <thead>
        <tr><th>Time</th><th>Symbol</th><th>Technical</th><th>Fundamental</th><th>Sentiment</th><th>Decision</th><th>Confidence</th></tr>
    </thead>
    <tbody>
        {% for s in signals %}
        <tr>
            <td>{{ s.timestamp.strftime('%H:%M') }}</td>
            <td>{{ s.symbol }}</td>
            <td class="{{ 'positive' if s.technical_score > 0 else 'negative' }}">{{ s.technical_score }}</td>
            <td class="{{ 'positive' if s.fundamental_score > 0 else 'negative' }}">{{ s.fundamental_score }}</td>
            <td class="{{ 'positive' if s.sentiment_score > 0 else 'negative' }}">{{ s.sentiment_score }}</td>
            <td>{{ s.decision }}</td>
            <td>{{ "{:.0f}".format(s.confidence * 100) }}%</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% else %}
<p class="empty-state">No signals generated yet</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 7: Create templates — settings.html**

```html
{% extends "base.html" %}
{% block content %}
<h1>Settings</h1>
<div class="settings-section">
    <h2>Agent Control</h2>
    <button hx-post="/api/agent/pause" class="btn-warning">Pause Agent</button>
    <button hx-post="/api/agent/resume" class="btn-success">Resume Agent</button>
</div>
<div class="settings-section">
    <h2>Risk Parameters</h2>
    <form hx-post="/api/settings/risk" hx-swap="none">
        <label>Max risk per trade (%)<input type="number" name="max_risk_per_trade" value="{{ settings.max_risk_per_trade }}" step="0.1" min="0.1" max="5"></label>
        <label>Max daily loss (%)<input type="number" name="max_daily_loss" value="{{ settings.max_daily_loss }}" step="0.1" min="0.5" max="10"></label>
        <label>Max portfolio heat (%)<input type="number" name="max_portfolio_heat" value="{{ settings.max_portfolio_heat }}" step="0.5" min="1" max="20"></label>
        <label>Max drawdown (%)<input type="number" name="max_drawdown" value="{{ settings.max_drawdown }}" step="0.5" min="2" max="20"></label>
        <label>Max sector exposure (%)<input type="number" name="max_sector_exposure" value="{{ settings.max_sector_exposure }}" step="1" min="5" max="50"></label>
        <label>Analysis interval (min)<input type="number" name="analysis_interval" value="{{ settings.analysis_interval }}" step="1" min="1" max="60"></label>
        <button type="submit">Save</button>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 8: Create templates — logs.html**

```html
{% extends "base.html" %}
{% block content %}
<h1>Logs</h1>
<div class="log-filters">
    <button hx-get="/api/logs?level=all" hx-target="#log-container">All</button>
    <button hx-get="/api/logs?level=TRADE" hx-target="#log-container">Trades</button>
    <button hx-get="/api/logs?level=WARNING" hx-target="#log-container">Warnings</button>
    <button hx-get="/api/logs?level=RISK_BLOCK" hx-target="#log-container">Risk Blocks</button>
</div>
<div id="log-container" class="log-container"
     hx-ext="sse" sse-connect="/api/logs/stream" sse-swap="message">
    {% for log in logs %}
    <div class="log-entry log-{{ log.level | lower }}">
        <span class="log-time">{{ log.timestamp }}</span>
        <span class="log-level">{{ log.level }}</span>
        <span class="log-msg">{{ log.message }}</span>
    </div>
    {% endfor %}
    {% if not logs %}
    <p class="empty-state">No logs yet</p>
    {% endif %}
</div>
{% endblock %}
```

- [ ] **Step 9: Add new routers to app.py**

Add imports and include_router calls in `src/api/app.py`:

```python
from src.api.routes.history import router as history_router
from src.api.routes.signals import router as signals_router
from src.api.routes.settings import router as settings_router
from src.api.routes.logs import router as logs_router

# Inside create_app(), add:
app.include_router(history_router)
app.include_router(signals_router)
app.include_router(settings_router)
app.include_router(logs_router)
```

- [ ] **Step 10: Commit**

```bash
cd ~/alpha-trader
git add src/api/
git commit -m "feat: dashboard pages — history, signals, settings, logs with HTMX"
```

---

## Task 14: Self-Maintenance — Health Checks, Auto-Healing, Data Cleanup

**Files:**
- Create: `src/core/maintenance.py`
- Create: `tests/test_core/test_maintenance.py`

- [ ] **Step 1: Write tests for maintenance logic**

Create `tests/test_core/test_maintenance.py`:

```python
from datetime import datetime, timedelta
from src.core.maintenance import (
    get_cleanup_cutoff,
    should_alert_no_cycles,
    HealthStatus,
    check_component_health,
)


def test_cleanup_cutoff_snapshots():
    cutoff = get_cleanup_cutoff("snapshots", now=datetime(2026, 4, 10))
    expected = datetime(2026, 1, 10)  # 90 days ago
    assert cutoff == expected


def test_cleanup_cutoff_logs():
    cutoff = get_cleanup_cutoff("logs", now=datetime(2026, 4, 10))
    expected = datetime(2026, 3, 11)  # 30 days ago
    assert cutoff == expected


def test_cleanup_cutoff_signals():
    cutoff = get_cleanup_cutoff("signals", now=datetime(2026, 4, 10))
    expected = datetime(2025, 10, 13)  # 180 days ago
    assert cutoff == expected


def test_should_alert_no_cycles_during_market():
    # Market hours, no cycle in 35 minutes -> alert
    last_cycle = datetime(2026, 4, 10, 10, 0)  # 10:00 ET
    now = datetime(2026, 4, 10, 10, 35)  # 10:35 ET
    assert should_alert_no_cycles(last_cycle, now, market_open=True) is True


def test_should_not_alert_recent_cycle():
    last_cycle = datetime(2026, 4, 10, 10, 0)
    now = datetime(2026, 4, 10, 10, 20)  # 20 min later
    assert should_alert_no_cycles(last_cycle, now, market_open=True) is False


def test_should_not_alert_outside_market():
    last_cycle = datetime(2026, 4, 10, 10, 0)
    now = datetime(2026, 4, 10, 18, 0)  # After hours
    assert should_alert_no_cycles(last_cycle, now, market_open=False) is False


def test_health_status_all_ok():
    status = HealthStatus(alpaca=True, claude=True, database=True, telegram=True)
    assert status.is_healthy is True


def test_health_status_degraded():
    status = HealthStatus(alpaca=True, claude=False, database=True, telegram=True)
    assert status.is_healthy is False
    assert "claude" in status.failed_components
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_core/test_maintenance.py -v
```

Expected: FAIL

- [ ] **Step 3: Create src/core/maintenance.py**

```python
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
            from src.config import settings
            executor = Executor(paper=settings.alpaca_paper)
            executor.get_account()
            return True
        elif component == "claude":
            import anthropic
            from src.config import settings
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
            from src.config import settings
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_core/test_maintenance.py -v
```

Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

```bash
cd ~/alpha-trader
git add src/core/maintenance.py tests/test_core/test_maintenance.py
git commit -m "feat: self-maintenance — health checks, data cleanup, cycle monitoring"
```

---

## Task 15: Screening — Watchlist Management

**Files:**
- Create: `src/utils/screening.py`
- Create: `tests/test_utils/__init__.py`
- Create: `tests/test_utils/test_screening.py`

- [ ] **Step 1: Write tests for screener**

Create `tests/test_utils/test_screening.py`:

```python
from src.utils.screening import filter_candidates, DEFAULT_WATCHLIST


def test_default_watchlist_not_empty():
    assert len(DEFAULT_WATCHLIST) >= 20


def test_filter_candidates_by_volume():
    candidates = [
        {"symbol": "AAPL", "avg_volume": 50_000_000, "market_cap": 3e12},
        {"symbol": "TINY", "avg_volume": 100_000, "market_cap": 500e6},  # Below 1M volume
        {"symbol": "MSFT", "avg_volume": 30_000_000, "market_cap": 2.5e12},
    ]
    result = filter_candidates(candidates, min_volume=1_000_000, min_market_cap=1e9)
    symbols = [c["symbol"] for c in result]
    assert "AAPL" in symbols
    assert "MSFT" in symbols
    assert "TINY" not in symbols


def test_filter_candidates_by_market_cap():
    candidates = [
        {"symbol": "AAPL", "avg_volume": 50_000_000, "market_cap": 3e12},
        {"symbol": "SMALL", "avg_volume": 5_000_000, "market_cap": 500e6},  # Below 1B cap
    ]
    result = filter_candidates(candidates, min_volume=1_000_000, min_market_cap=1e9)
    symbols = [c["symbol"] for c in result]
    assert "AAPL" in symbols
    assert "SMALL" not in symbols


def test_filter_respects_max_size():
    candidates = [
        {"symbol": f"SYM{i}", "avg_volume": 10_000_000, "market_cap": 5e9}
        for i in range(100)
    ]
    result = filter_candidates(candidates, max_symbols=50)
    assert len(result) == 50
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/alpha-trader
uv run pytest tests/test_utils/test_screening.py -v
```

Expected: FAIL

- [ ] **Step 3: Create src/utils/screening.py**

```python
DEFAULT_WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "JNJ",
    "WMT", "PG", "UNH", "HD", "MA", "DIS", "NFLX", "PYPL", "ADBE", "CRM",
    "INTC", "AMD", "QCOM", "AVGO", "COST", "PEP", "KO", "MRK", "ABBV", "LLY",
]


def filter_candidates(
    candidates: list[dict],
    min_volume: int = 1_000_000,
    min_market_cap: float = 1e9,
    max_symbols: int = 50,
) -> list[dict]:
    """Filter stock candidates by volume and market cap."""
    filtered = [
        c for c in candidates
        if c.get("avg_volume", 0) >= min_volume
        and c.get("market_cap", 0) >= min_market_cap
    ]
    # Sort by volume descending, take top N
    filtered.sort(key=lambda c: c.get("avg_volume", 0), reverse=True)
    return filtered[:max_symbols]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/alpha-trader
uv run pytest tests/test_utils/test_screening.py -v
```

Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
cd ~/alpha-trader
git add src/utils/screening.py tests/test_utils/
git commit -m "feat: stock screening with volume, market cap filters, default watchlist"
```

---

## Task 16: Docker + Railway Deploy Configuration

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `railway.toml`
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy source
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

# Expose dashboard port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run
CMD ["uv", "run", "python", "-m", "src.main"]
```

- [ ] **Step 2: Create docker-compose.yml**

```yaml
services:
  app:
    build: .
    restart: always
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_DB: alpha_trader
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

- [ ] **Step 3: Create railway.toml**

```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uv run python -m src.main"
healthcheckPath = "/health"
healthcheckTimeout = 60
restartPolicyType = "always"
```

- [ ] **Step 4: Create .github/workflows/ci.yml**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Lint
        run: uv run ruff check src/ tests/

      - name: Test
        run: uv run pytest tests/ -v --tb=short
        env:
          ALPACA_API_KEY: fake
          ALPACA_SECRET_KEY: fake
          ANTHROPIC_API_KEY: fake
          DATABASE_URL: sqlite+aiosqlite:///test.db
```

- [ ] **Step 5: Commit**

```bash
cd ~/alpha-trader
git add Dockerfile docker-compose.yml railway.toml .github/
git commit -m "feat: Docker, docker-compose, Railway config, GitHub Actions CI"
```

---

## Task 17: Integration — Wire Dashboard to Real Data + Final Main

**Files:**
- Modify: `src/api/app.py` — inject portfolio/executor dependencies
- Modify: `src/api/routes/dashboard.py` — use real portfolio data
- Modify: `src/api/routes/positions.py` — use real executor data
- Modify: `src/main.py` — start FastAPI alongside scheduler

- [ ] **Step 1: Update src/api/app.py to accept dependencies**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.positions import router as positions_router
from src.api.routes.history import router as history_router
from src.api.routes.signals import router as signals_router
from src.api.routes.settings import router as settings_router
from src.api.routes.logs import router as logs_router


def create_app(portfolio=None, executor=None) -> FastAPI:
    app = FastAPI(title="Alpha Trader", version="0.1.0")

    # Store shared state
    app.state.portfolio = portfolio
    app.state.executor = executor

    # Static files
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "alpha-trader"}

    # API endpoints for HTMX actions
    @app.post("/api/close/{symbol}")
    async def close_position(symbol: str):
        if app.state.executor:
            result = await app.state.executor.close_position(symbol)
            return result
        return {"status": "error", "error": "executor not available"}

    @app.post("/api/agent/pause")
    async def pause_agent():
        return {"status": "paused"}

    @app.post("/api/agent/resume")
    async def resume_agent():
        return {"status": "active"}

    app.include_router(dashboard_router)
    app.include_router(positions_router)
    app.include_router(history_router)
    app.include_router(signals_router)
    app.include_router(settings_router)
    app.include_router(logs_router)

    return app
```

- [ ] **Step 2: Update src/api/routes/dashboard.py to use real data**

```python
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/")
async def overview(request: Request):
    portfolio = request.app.state.portfolio
    if portfolio:
        state = portfolio.get_state()
        context = {
            "request": request,
            "status": "ACTIVE",
            "equity": state["equity"],
            "daily_pnl": state["daily_pnl"],
            "total_pnl": state["equity"] - 100_000,
            "drawdown_pct": state["drawdown_pct"] * 100,
            "positions_count": len(state["positions"]),
            "portfolio_heat": state["portfolio_heat"],
        }
    else:
        context = {
            "request": request,
            "status": "OFFLINE",
            "equity": 0, "daily_pnl": 0, "total_pnl": 0,
            "drawdown_pct": 0, "positions_count": 0, "portfolio_heat": 0,
        }
    return templates.TemplateResponse("overview.html", context)
```

- [ ] **Step 3: Update src/main.py to run FastAPI alongside scheduler**

Add to the end of `main()` in `src/main.py`, before `await stop_event.wait()`:

```python
    # Start FastAPI in background
    import uvicorn
    from src.api.app import create_app

    app = create_app(portfolio=portfolio, executor=executor)
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    # Run server as a task
    server_task = asyncio.create_task(server.serve())
    logger.info("Dashboard running at http://0.0.0.0:8000")
```

- [ ] **Step 4: Commit**

```bash
cd ~/alpha-trader
git add src/api/ src/main.py
git commit -m "feat: wire dashboard to real portfolio data, run FastAPI with scheduler"
```

---

## Task 18: Run All Tests and Final Verification

- [ ] **Step 1: Run full test suite**

```bash
cd ~/alpha-trader
uv run pytest tests/ -v --tb=short
```

Expected: All tests PASS

- [ ] **Step 2: Run linter**

```bash
cd ~/alpha-trader
uv run ruff check src/ tests/
```

Fix any issues found.

- [ ] **Step 3: Verify Docker builds**

```bash
cd ~/alpha-trader
docker build -t alpha-trader .
```

Expected: Build succeeds

- [ ] **Step 4: Create README.md**

```markdown
# Alpha Trader

Autonomous stock trading agent with professional 5-level risk management.

## Quick Start

```bash
# Clone and install
git clone https://github.com/naattiiiiii/alpha-trader.git
cd alpha-trader
cp .env.example .env  # Fill in your API keys
uv sync

# Run with Docker
docker compose up

# Or run directly
uv run python -m src.main
```

## Dashboard

Visit `http://localhost:8000` after starting.

## Configuration

Edit `.env` or use the Settings page in the dashboard.

## Paper Trading

Set `ALPACA_PAPER=true` in `.env` (default). Get API keys at https://alpaca.markets.
```

- [ ] **Step 5: Final commit**

```bash
cd ~/alpha-trader
git add README.md
git commit -m "docs: add README with quick start guide"
```

- [ ] **Step 6: Push to GitHub**

```bash
cd ~/alpha-trader
gh repo create naattiiiiii/alpha-trader --private --source=. --push
```
