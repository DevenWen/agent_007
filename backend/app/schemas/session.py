"""Session Schemas"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.models.session import SessionStatus
from app.models.message import MessageRole


class MessageResponse(BaseModel):
    """Message 响应"""

    id: int
    role: MessageRole
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True


class SessionSummary(BaseModel):
    """Session 摘要（列表用）"""

    id: str
    ticket_id: str
    status: SessionStatus
    message_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    """Session 详情响应"""

    id: str
    ticket_id: str
    status: SessionStatus
    context: Optional[dict[str, Any]] = None
    messages: List[MessageResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AddMessageRequest(BaseModel):
    """添加消息请求（人工介入）"""

    content: str = Field(..., min_length=1)
