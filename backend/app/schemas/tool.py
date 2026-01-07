"""Tool Schemas"""

import json
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class ToolResponse(BaseModel):
    """Tool 详情响应"""

    id: str
    name: str
    description: Optional[str] = None
    schema_: dict[str, Any] = Field(default_factory=dict, alias="schema")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

    @field_validator("schema_", mode="before")
    @classmethod
    def parse_schema(cls, v):
        """Parse JSON string to dict if needed"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v or {}


class ToolSummary(BaseModel):
    """Tool 简要信息"""

    id: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
