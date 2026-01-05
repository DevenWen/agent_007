import json
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.tool import Tool
from app.tools.registry import get_all_registered_tools

logger = logging.getLogger(__name__)


async def sync_tools_to_database(db: AsyncSession) -> dict:
    """
    同步注册的 Tools 到数据库

    Returns:
        dict: Sync result summary
    """
    result = {"created": [], "updated": [], "unchanged": []}

    registered_tools = get_all_registered_tools()

    for name, tool_def in registered_tools.items():
        # 查找现有记录
        stmt = select(Tool).where(Tool.name == name)
        existing = (await db.execute(stmt)).scalar_one_or_none()

        # 确保 schema 是 JSON 字符串
        schema_json = json.dumps(tool_def.input_schema)

        if existing is None:
            # 创建新记录
            new_tool = Tool(
                id=str(uuid.uuid4()),
                name=name,
                description=tool_def.description,
                schema=schema_json,
            )
            db.add(new_tool)
            result["created"].append(name)
        else:
            # 检查是否需要更新
            # 注意：这里简化对比，只对比 description 和 schema 字符串
            # 实际生产可能需要解析 JSON 对比
            if (
                existing.description != tool_def.description
                or existing.schema != schema_json
            ):
                existing.description = tool_def.description
                existing.schema = schema_json
                result["updated"].append(name)
            else:
                result["unchanged"].append(name)

    await db.commit()
    logger.info(f"Tools synchronization completed: {result}")
    return result
