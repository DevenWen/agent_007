"""Tools API Router"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.tool import Tool
from app.schemas.tool import ToolResponse

router = APIRouter(prefix="/tools", tags=["Tools"])


@router.get("", response_model=List[ToolResponse])
async def list_tools(db: AsyncSession = Depends(get_db)):
    """获取所有 Tool 列表"""
    result = await db.execute(select(Tool).order_by(Tool.name))
    tools = result.scalars().all()
    return [ToolResponse.model_validate(t) for t in tools]


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(tool_id: str, db: AsyncSession = Depends(get_db)):
    """获取 Tool 详情"""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    return ToolResponse.model_validate(tool)
