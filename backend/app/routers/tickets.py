"""Tickets API Router"""

import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.agent import Agent
from app.models.ticket import Ticket, TicketStatus
from app.models.session import Session, SessionStatus
from app.models.step import Step
from app.schemas.ticket import (
    TicketSummary,
    TicketResponse,
    CreateTicketRequest,
    StepResponse,
    SessionSummary,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


def _build_ticket_response(ticket: Ticket) -> TicketResponse:
    """构建 Ticket 响应"""
    # 找到当前活跃的 Session
    current_session = next(
        (
            s
            for s in ticket.sessions
            if s.status in [SessionStatus.ACTIVE, SessionStatus.SUSPENDED]
        ),
        None,
    )

    # 解析 JSON 字段
    params = json.loads(ticket.params) if ticket.params else None
    context = json.loads(ticket.context) if ticket.context else None

    # 构建 Steps
    steps = []
    for step in sorted(ticket.steps, key=lambda s: s.idx):
        # 安全解析 result，如果不是有效 JSON 则设为 None
        step_result = None
        if step.result:
            try:
                parsed = json.loads(step.result)
                if isinstance(parsed, dict):
                    step_result = parsed
            except (json.JSONDecodeError, TypeError):
                pass
        steps.append(
            StepResponse(
                idx=step.idx,
                title=step.title,
                status=step.status,
                result=step_result,
                created_at=step.created_at,
                updated_at=step.updated_at,
            )
        )

    # 构建 Sessions 摘要
    # 按创建时间倒序
    sessions_summary = [
        SessionSummary.model_validate(s)
        for s in sorted(ticket.sessions, key=lambda x: x.created_at, reverse=True)
    ]

    return TicketResponse(
        id=ticket.id,
        agent_id=ticket.agent_id,
        agent_name=ticket.agent.name,
        status=ticket.status,
        params=params,
        context=context,
        error_message=ticket.error_message,
        steps=steps,
        sessions=sessions_summary,  # 新增
        current_session_id=current_session.id if current_session else None,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


@router.get("", response_model=List[TicketSummary])
async def list_tickets(
    status: Optional[TicketStatus] = Query(None),
    agent_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """获取 Ticket 列表"""
    query = select(Ticket).options(selectinload(Ticket.agent))

    if status:
        query = query.where(Ticket.status == status.value)
    if agent_id:
        query = query.where(Ticket.agent_id == agent_id)

    query = query.order_by(Ticket.updated_at.desc())
    result = await db.execute(query)
    tickets = result.scalars().all()

    return [
        TicketSummary(
            id=t.id,
            agent_id=t.agent_id,
            agent_name=t.agent.name,
            status=t.status,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
        for t in tickets
    ]


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, db: AsyncSession = Depends(get_db)):
    """获取 Ticket 详情"""
    result = await db.execute(
        select(Ticket)
        .options(
            selectinload(Ticket.agent),
            selectinload(Ticket.sessions),
            selectinload(Ticket.steps),
        )
        .where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return _build_ticket_response(ticket)


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(req: CreateTicketRequest, db: AsyncSession = Depends(get_db)):
    """创建 Ticket"""
    # 验证 Agent 存在
    result = await db.execute(select(Agent).where(Agent.id == req.agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    ticket = Ticket(
        id=str(uuid.uuid4()),
        agent_id=req.agent_id,
        status=TicketStatus.PENDING.value,
        params=json.dumps(req.params) if req.params else None,
        context=json.dumps(req.context) if req.context else None,
    )

    db.add(ticket)
    await db.flush()

    # 重新加载关系
    result = await db.execute(
        select(Ticket)
        .options(
            selectinload(Ticket.agent),
            selectinload(Ticket.sessions),
            selectinload(Ticket.steps),
        )
        .where(Ticket.id == ticket.id)
    )
    ticket = result.scalar_one()

    return _build_ticket_response(ticket)


@router.patch("/{ticket_id}/resume", response_model=TicketResponse)
async def resume_ticket(ticket_id: str, db: AsyncSession = Depends(get_db)):
    """恢复挂起的 Ticket（继续原 Session）"""
    result = await db.execute(
        select(Ticket)
        .options(
            selectinload(Ticket.agent),
            selectinload(Ticket.sessions),
            selectinload(Ticket.steps),
        )
        .where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.status != TicketStatus.SUSPENDED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resume ticket with status '{ticket.status}'",
        )

    # 恢复 Ticket 和 Session 状态
    ticket.status = TicketStatus.RUNNING.value
    for session in ticket.sessions:
        if session.status == SessionStatus.SUSPENDED.value:
            session.status = SessionStatus.ACTIVE.value

            # TODO: 这里应该通知 Scheduler 继续执行
            # 目前 MVP 暂时依赖前端轮询或后台自动检测

    await db.flush()
    return _build_ticket_response(ticket)


@router.patch("/{ticket_id}/reset", response_model=TicketResponse)
async def reset_ticket(ticket_id: str, db: AsyncSession = Depends(get_db)):
    """重置 Ticket（创建新 Session）"""
    result = await db.execute(
        select(Ticket)
        .options(
            selectinload(Ticket.agent),
            selectinload(Ticket.sessions),
            selectinload(Ticket.steps),
        )
        .where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # 归档当前 Session
    for session in ticket.sessions:
        if session.status in [
            SessionStatus.ACTIVE.value,
            SessionStatus.SUSPENDED.value,
        ]:
            session.status = SessionStatus.COMPLETED.value

    # 重置 Ticket 状态
    ticket.status = TicketStatus.PENDING.value
    ticket.error_message = None

    await db.flush()
    return _build_ticket_response(ticket)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(ticket_id: str, db: AsyncSession = Depends(get_db)):
    """删除 Ticket"""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    await db.delete(ticket)
