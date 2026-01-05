"""Ticket Model"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.session import Session
    from app.models.step import Step


class TicketStatus(str, Enum):
    """Ticket 状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"


class Ticket(Base):
    """Ticket 工单聚合根"""

    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    agent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agents.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default=TicketStatus.PENDING.value, nullable=False
    )
    params: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    context: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    agent: Mapped["Agent"] = relationship("Agent", back_populates="tickets")
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="ticket", cascade="all, delete-orphan"
    )
    steps: Mapped[List["Step"]] = relationship(
        "Step", back_populates="ticket", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Ticket(id={self.id[:8]}, status={self.status})>"
