"""Agent Schemas"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import json

from pydantic import BaseModel, Field, field_validator
from app.schemas.tool import ToolResponse


class AgentBase(BaseModel):
    """Agent 基础模型"""

    name: str = Field(..., min_length=1, max_length=100, description="Agent 名称")
    description: Optional[str] = Field(None, description="Agent 描述")
    prompt: str = Field(..., description="Agent 提示词")
    params_schema: Optional[str] = Field(None, description="参数 JSON Schema")

    # PRD 0.0.3: Skill System 新增字段
    skill_name: Optional[str] = Field(None, description="关联的 Skill 名称")
    max_iterations: int = Field(10, description="最大执行迭代次数", ge=1, le=100)
    default_params: Optional[Dict[str, Any]] = Field(None, description="默认参数")
    tool_names: Optional[List[str]] = Field(None, description="工具名称列表")


class AgentCreate(AgentBase):
    """创建 Agent 请求模型"""

    pass


class AgentUpdate(BaseModel):
    """更新 Agent 请求模型"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    prompt: Optional[str] = None
    params_schema: Optional[str] = None
    skill_name: Optional[str] = None
    max_iterations: Optional[int] = Field(None, ge=1, le=100)
    default_params: Optional[Dict[str, Any]] = None
    tool_names: Optional[List[str]] = None


class AgentToolUpdate(BaseModel):
    """更新 Agent 关联的 Tools"""

    tool_ids: List[str] = Field(..., description="Tool ID 列表")


class AgentResponse(AgentBase):
    """Agent 响应模型"""

    id: str
    created_at: datetime
    updated_at: datetime
    tools: List["ToolResponse"] = Field(
        default_factory=list, description="关联的 Tools 列表"
    )

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
