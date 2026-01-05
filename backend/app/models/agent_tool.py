"""Agent-Tool Many-to-Many Association Table"""

from sqlalchemy import Table, Column, String, ForeignKey

from app.database import Base


agent_tools = Table(
    "agent_tools",
    Base.metadata,
    Column(
        "agent_id",
        String(36),
        ForeignKey("agents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tool_id",
        String(36),
        ForeignKey("tools.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
