"""Agent Model"""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.tool import Tool
    from app.models.ticket import Ticket


class Agent(Base):
    """Agent 代理实体"""

    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    # 新增 params_schema 字段，存储 JSON 字符串
    params_schema: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系：多对多关联 Tools
    tools: Mapped[List["Tool"]] = relationship(
        "Tool",
        secondary="agent_tools",
        back_populates="agents",
    )

    # 关系：一对多关联 Tickets
    tickets: Mapped[List["Ticket"]] = relationship(
        "Ticket",
        back_populates="agent",
    )

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name={self.name})>"
