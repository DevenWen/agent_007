"""Agent Schemas"""

from datetime import datetime
from typing import List, Optional, Any, Dict
import json

from pydantic import BaseModel, Field, field_validator
from .tool import ToolSummary


class AgentSummary(BaseModel):
    """Agent 摘要（列表用）"""

    id: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class AgentResponse(BaseModel):
    """Agent 详情响应"""

    id: str
    name: str
    description: Optional[str] = None
    prompt: str
    params_schema: Optional[Dict[str, Any]] = None  # 返回解析后的 JSON 对象
    tool_ids: List[str] = Field(default_factory=list)
    tools: List[ToolSummary] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_validator("params_schema", mode="before")
    def parse_params_schema(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v


class CreateAgentRequest(BaseModel):
    """创建 Agent 请求"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    prompt: str = Field(..., min_length=1)
    params_schema: Optional[Dict[str, Any]] = None  # 接收 JSON 对象
    tool_ids: List[str] = Field(default_factory=list)


class UpdateAgentRequest(BaseModel):
    """更新 Agent 请求"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    prompt: Optional[str] = Field(None, min_length=1)
    params_schema: Optional[Dict[str, Any]] = None
    tool_ids: Optional[List[str]] = None
