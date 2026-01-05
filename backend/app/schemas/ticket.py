"""Ticket Schemas"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.models.ticket import TicketStatus
from app.models.step import StepStatus
from app.models.session import SessionStatus


class StepResponse(BaseModel):
    """Step 响应"""

    index: int = Field(alias="idx")
    title: str
    status: StepStatus
    result: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class SessionSummary(BaseModel):
    """Session 摘要"""

    id: str
    status: SessionStatus
    created_at: datetime

    class Config:
        from_attributes = True


class TicketSummary(BaseModel):
    """Ticket 摘要（列表用）"""

    id: str
    agent_id: str
    agent_name: str
    status: TicketStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    """Ticket 详情响应"""

    id: str
    agent_id: str
    agent_name: str
    status: TicketStatus
    params: Optional[dict[str, Any]] = None
    context: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    steps: List[StepResponse] = Field(default_factory=list)
    sessions: List[SessionSummary] = Field(default_factory=list)  # 新增
    current_session_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateTicketRequest(BaseModel):
    """创建 Ticket 请求"""

    agent_id: str
    params: Optional[dict[str, Any]] = None
    context: Optional[dict[str, Any]] = None
