"""Prompt Compiler Service

Implements the Prompt Merge Strategy for Skill System.
Final Prompt = System Prompt + Skill Content + Agent Prompt (rendered with params)
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from jinja2 import Template, TemplateError

from app.services.skill_loader import SkillLoader

logger = logging.getLogger(__name__)

# Global System Prompt path
SYSTEM_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompt" / "system_prompt.md"

# Skill directory
SKILL_DIR = Path(__file__).parent.parent.parent / "prompt" / "skill"


def load_system_prompt() -> str:
    """加载全局 System Prompt

    Returns:
        System Prompt 内容，如果文件不存在返回空字符串
    """
    if SYSTEM_PROMPT_PATH.exists():
        return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    logger.warning(f"System prompt file not found: {SYSTEM_PROMPT_PATH}")
    return ""


def render_agent_prompt(agent_prompt: str, params: Dict[str, Any]) -> str:
    """使用 Jinja2 渲染 Agent Prompt

    Args:
        agent_prompt: Agent 的原始 prompt 模板
        params: 用于渲染的参数

    Returns:
        渲染后的 prompt
    """
    if not agent_prompt:
        return ""

    try:
        template = Template(agent_prompt)
        return template.render(**params)
    except TemplateError as e:
        logger.error(f"Failed to render agent prompt: {e}")
        # 如果渲染失败，返回原始 prompt
        return agent_prompt


def compile_system_message(
    skill_name: Optional[str], agent_prompt: str, params: Dict[str, Any]
) -> str:
    """编译完整的 System Message

    Merge Strategy:
    1. System Prompt (Global)
    2. Skill Content (Base Template)
    3. Agent Prompt (Override/Customization, rendered with params)

    Args:
        skill_name: Agent 关联的 Skill 名称
        agent_prompt: Agent 的自定义 prompt
        params: 用于渲染 Agent prompt 的参数

    Returns:
        合并后的完整 system message
    """
    parts = []

    # 1. System Prompt
    system_prompt = load_system_prompt()
    if system_prompt:
        parts.append(system_prompt.strip())

    # 2. Skill Content
    if skill_name:
        skill_loader = SkillLoader(SKILL_DIR)
        skill = skill_loader.get_skill(skill_name)
        if skill:
            parts.append(f"--- Skill: {skill.name} ---")
            parts.append(skill.content.strip())
        else:
            logger.warning(f"Skill not found: {skill_name}")

    # 3. Agent Prompt (rendered)
    rendered_agent_prompt = render_agent_prompt(agent_prompt, params)
    if rendered_agent_prompt:
        parts.append("--- Specific Instructions ---")
        parts.append(rendered_agent_prompt.strip())

    return "\n\n".join(parts)


def get_effective_tools(
    skill_name: Optional[str], agent_tool_names: Optional[List[str]]
) -> List[str]:
    """获取有效的 Tool 列表 (Union Logic)

    Args:
        skill_name: Agent 关联的 Skill 名称
        agent_tool_names: Agent 额外配置的工具名称

    Returns:
        去重后的工具名称列表
    """
    tools = set()

    # 1. Skill Tools
    if skill_name:
        skill_loader = SkillLoader(SKILL_DIR)
        skill = skill_loader.get_skill(skill_name)
        if skill:
            tools.update(skill.tools)

    # 2. Agent Tools (union)
    if agent_tool_names:
        tools.update(agent_tool_names)

    return list(tools)
