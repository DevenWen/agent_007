"""Agents API Router"""

import uuid
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.agent import Agent
from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
)

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=List[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    """获取所有 Agent 列表"""
    result = await db.execute(
        select(Agent)
        .options(selectinload(Agent.tools))
        .order_by(Agent.created_at.desc())
    )
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

    return agent


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(req: AgentCreate, db: AsyncSession = Depends(get_db)):
    """创建 Agent"""
    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"Creating agent with skill_name: {req.skill_name}")

    agent = Agent(
        id=str(uuid.uuid4()),
        name=req.name,
        description=req.description,
        prompt=req.prompt,
        params_schema=req.params_schema,
        skill_name=req.skill_name,
        max_iterations=req.max_iterations,
        default_params=json.dumps(req.default_params) if req.default_params else None,
        tool_names=json.dumps(req.tool_names) if req.tool_names else None,
    )

    db.add(agent)
    await db.commit()
    await db.refresh(agent, ["tools"])

    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str, req: AgentUpdate, db: AsyncSession = Depends(get_db)
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
    if req.params_schema is not None:
        agent.params_schema = req.params_schema
    if req.skill_name is not None:
        agent.skill_name = req.skill_name
    if req.max_iterations is not None:
        agent.max_iterations = req.max_iterations
    if req.default_params is not None:
        agent.default_params = json.dumps(req.default_params)
    if req.tool_names is not None:
        agent.tool_names = json.dumps(req.tool_names)

    await db.commit()
    await db.refresh(agent, ["tools"])

    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """删除 Agent"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await db.delete(agent)
    await db.commit()
