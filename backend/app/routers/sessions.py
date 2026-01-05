"""Sessions API Router"""

import json
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.session import Session, SessionStatus
from app.models.message import Message, MessageRole
from app.models.ticket import Ticket, TicketStatus
from app.schemas.session import (
    SessionSummary,
    SessionResponse,
    MessageResponse,
    AddMessageRequest,
)

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("", response_model=List[SessionSummary])
async def list_sessions(
    ticket_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """获取 Session 列表"""
    query = select(Session)

    if ticket_id:
        query = query.where(Session.ticket_id == ticket_id)

    query = query.order_by(Session.updated_at.desc())
    result = await db.execute(query)
    sessions = result.scalars().all()

    # 获取每个 Session 的消息数量
    summaries = []
    for s in sessions:
        msg_count_result = await db.execute(
            select(func.count(Message.id)).where(Message.session_id == s.id)
        )
        msg_count = msg_count_result.scalar() or 0

        summaries.append(
            SessionSummary(
                id=s.id,
                ticket_id=s.ticket_id,
                status=s.status,
                message_count=msg_count,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
        )

    return summaries


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """获取 Session 详情"""
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.messages))
        .where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 解析 context JSON
    context = json.loads(session.context) if session.context else None

    # 按时间排序消息
    messages = sorted(session.messages, key=lambda m: m.timestamp)

    return SessionResponse(
        id=session.id,
        ticket_id=session.ticket_id,
        status=session.status,
        context=context,
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                timestamp=m.timestamp,
            )
            for m in messages
        ],
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.post(
    "/{session_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_message(
    session_id: str,
    req: AddMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """添加消息（人工介入回复）"""
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.ticket))
        .where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 创建消息
    message = Message(
        session_id=session_id,
        role=MessageRole.USER.value,
        content=req.content,
        timestamp=datetime.utcnow(),
    )
    db.add(message)

    # 如果 Session 处于 suspended 状态，自动恢复
    if session.status == SessionStatus.SUSPENDED.value:
        session.status = SessionStatus.ACTIVE.value
        if session.ticket.status == TicketStatus.SUSPENDED.value:
            session.ticket.status = TicketStatus.RUNNING.value

    await db.flush()

    return MessageResponse(
        id=message.id,
        role=message.role,
        content=message.content,
        timestamp=message.timestamp,
    )
