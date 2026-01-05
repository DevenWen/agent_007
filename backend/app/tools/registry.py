from typing import Callable, Any, Awaitable, Dict
from functools import wraps
from claude_agent_sdk import tool as sdk_tool

# 全局注册表（用于数据库同步）
# Key: tool name
# Value: ToolDefinition
_TOOL_REGISTRY: Dict[str, "ToolDefinition"] = {}


class ToolDefinition:
    """工具定义"""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict,
        sdk_tool_func: Callable,  # SDK 包装后的函数
        original_func: Callable,  # 原始函数
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.sdk_tool_func = sdk_tool_func
        self.original_func = original_func


def register_tool(
    name: str,
    description: str,
    input_schema: dict[str, type] | dict,
):
    """
    统一工具注册装饰器

    同时完成:
    1. 注册到 claude_agent_sdk（运行时调用）
    2. 注册到 _TOOL_REGISTRY（数据库同步）

    目前支持的 input_schema 格式：
    SDK 简写格式: {"path": str, "content": str}
    """

    def decorator(func: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]):
        # 1. 使用 SDK 的 @tool 装饰器包装
        # sdk_tool 会处理 input_schema 的格式转换
        sdk_wrapped = sdk_tool(name, description, input_schema)(func)

        # 2. 转换 input_schema 为 JSON Schema 格式（用于数据库存储）
        json_schema = _convert_to_json_schema(input_schema)

        # 3. 注册到全局注册表
        _TOOL_REGISTRY[name] = ToolDefinition(
            name=name,
            description=description,
            input_schema=json_schema,
            sdk_tool_func=sdk_wrapped,
            original_func=func,
        )

        # 返回 SDK 包装后的函数，以便在那直接使用
        return sdk_wrapped

    return decorator


def _convert_to_json_schema(input_schema: dict[str, type] | dict) -> dict:
    """
    将 SDK 格式的 schema 转换为 JSON Schema 格式

    SDK 格式: {"name": str, "age": int}
    JSON Schema: {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"]
    }
    """
    # 如果已经是 JSON Schema 格式（通常包含 properties），直接返回
    if "type" in input_schema and input_schema.get("type") == "object":
        return input_schema
    if "properties" in input_schema:
        return {
            "type": "object",
            "properties": input_schema,
            # 简易处理：假设所有字段都必填，如果不是标准 json schema
            "required": list(input_schema.keys()),
        }

    # 类型映射
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    properties = {}
    required = []

    for field_name, field_type in input_schema.items():
        # 处理 Optional/Union 等复杂类型暂且简化，假设都是基础类型
        json_type = type_map.get(field_type, "string")
        properties[field_name] = {"type": json_type}
        required.append(field_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def get_all_registered_tools() -> dict[str, ToolDefinition]:
    """获取所有注册的工具"""
    return _TOOL_REGISTRY.copy()


def get_sdk_tools_for_agent(tool_names: list[str]) -> list[Callable]:
    """获取 Agent 可用的 SDK 工具函数列表"""
    tools = []
    for name in tool_names:
        if name in _TOOL_REGISTRY:
            tools.append(_TOOL_REGISTRY[name].sdk_tool_func)
    return tools
