"""Agents API Router"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.agent import Agent
from app.models.tool import Tool
from app.schemas.agent import (
    AgentSummary,
    AgentResponse,
    CreateAgentRequest,
    UpdateAgentRequest,
)
from app.schemas.tool import ToolSummary

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=List[AgentSummary])
async def list_agents(db: AsyncSession = Depends(get_db)):
    """获取所有 Agent 列表"""
    result = await db.execute(select(Agent).order_by(Agent.created_at.desc()))
    agents = result.scalars().all()
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """获取 Agent 详情"""
    result = await db.execute(
        select(Agent).options(selectinload(Agent.tools)).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        prompt=agent.prompt,
        tool_ids=[t.id for t in agent.tools],
        tools=[ToolSummary.model_validate(t) for t in agent.tools],
        created_at=agent.created_at,
        updated_at=agent.updated_at,
    )


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(req: CreateAgentRequest, db: AsyncSession = Depends(get_db)):
    """创建 Agent"""
    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"Creating agent with tool_ids: {req.tool_ids}")

    agent = Agent(
        id=str(uuid.uuid4()),
        name=req.name,
        description=req.description,
        prompt=req.prompt,
    )

    # 关联 Tools
    tools_list = []
    if req.tool_ids:
        result = await db.execute(select(Tool).where(Tool.id.in_(req.tool_ids)))
        tools = result.scalars().all()
        logger.info(f"Found {len(tools)} tools from DB: {[t.id for t in tools]}")
        tools_list = list(tools)
        agent.tools = tools_list

    logger.info(f"Agent tools after assignment: {[t.id for t in tools_list]}")

    db.add(agent)
    await db.flush()

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        prompt=agent.prompt,
        tool_ids=[t.id for t in tools_list],
        tools=[ToolSummary.model_validate(t) for t in tools_list],
        created_at=agent.created_at,
        updated_at=agent.updated_at,
    )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str, req: UpdateAgentRequest, db: AsyncSession = Depends(get_db)
):
    """更新 Agent"""
    result = await db.execute(
        select(Agent).options(selectinload(Agent.tools)).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 更新字段
    if req.name is not None:
        agent.name = req.name
    if req.description is not None:
        agent.description = req.description
    if req.prompt is not None:
        agent.prompt = req.prompt
    if req.tool_ids is not None:
        result = await db.execute(select(Tool).where(Tool.id.in_(req.tool_ids)))
        tools = result.scalars().all()
        agent.tools = list(tools)

    await db.flush()

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        prompt=agent.prompt,
        tool_ids=[t.id for t in agent.tools],
        tools=[ToolSummary.model_validate(t) for t in agent.tools],
        created_at=agent.created_at,
        updated_at=agent.updated_at,
    )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """删除 Agent"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await db.delete(agent)
