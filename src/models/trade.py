from datetime import datetime
from sqlalchemy import String, Float, DateTime, Enum as SAEnum
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
