"""Tool Schemas"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ToolResponse(BaseModel):
    """Tool 详情响应"""

    id: str
    name: str
    description: Optional[str] = None
    schema_: dict[str, Any]  # 避免与 pydantic schema 冲突
    created_at: datetime

    class Config:
        from_attributes = True
        # 映射 ORM 字段名
        populate_by_name = True

    @classmethod
    def from_orm_with_schema(cls, tool):
        """从 ORM 对象创建，解析 schema JSON"""
        import json

        return cls(
            id=tool.id,
            name=tool.name,
            description=tool.description,
            schema_=json.loads(tool.schema) if tool.schema else {},
            created_at=tool.created_at,
        )


class ToolSummary(BaseModel):
    """Tool 简要信息"""

    id: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
