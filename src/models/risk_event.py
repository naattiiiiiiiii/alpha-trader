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
    level: Mapped[str] = mapped_column(String(20))
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
