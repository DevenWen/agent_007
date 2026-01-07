"""Skills API Router

提供 Skill 查询接口
"""

from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.skill_loader import SkillLoader, Skill as SkillData


router = APIRouter(prefix="/skills", tags=["skills"])

# 初始化 SkillLoader (指向 prompt/skill 目录)
SKILL_DIR = Path(__file__).parent.parent.parent / "prompt" / "skill"
skill_loader = SkillLoader(SKILL_DIR)


class SkillResponse(BaseModel):
    """Skill 响应模型"""

    name: str
    description: str
    tools: List[str]
    content: str


class SkillListItem(BaseModel):
    """Skill 列表项"""

    name: str
    description: str
    tools: List[str]


@router.get("", response_model=List[SkillListItem])
async def list_skills():
    """列出所有可用的 Skills

    Returns:
        Skill 列表(不包含 content)
    """
    skills = skill_loader.list_skills()
    return [
        SkillListItem(name=skill.name, description=skill.description, tools=skill.tools)
        for skill in skills
    ]


@router.get("/{name}", response_model=SkillResponse)
async def get_skill(name: str):
    """获取指定 Skill 的详细信息

    Args:
        name: Skill 名称

    Returns:
        完整的 Skill 信息

    Raises:
        HTTPException: 如果 Skill 不存在
    """
    skill = skill_loader.get_skill(name)

    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{name}' not found")

    return SkillResponse(
        name=skill.name,
        description=skill.description,
        tools=skill.tools,
        content=skill.content,
    )
