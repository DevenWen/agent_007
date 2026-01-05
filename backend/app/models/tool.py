"""Tool Model"""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.agent import Agent


class Tool(Base):
    """Tool 工具实体"""

    __tablename__ = "tools"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    schema: Mapped[str] = mapped_column(Text, nullable=False)  # JSON Schema
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系：多对多关联 Agents
    agents: Mapped[List["Agent"]] = relationship(
        "Agent",
        secondary="agent_tools",
        back_populates="tools",
    )

    def __repr__(self) -> str:
        return f"<Tool(id={self.id}, name={self.name})>"
