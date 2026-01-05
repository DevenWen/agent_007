"""Tools Package - 内置工具实现"""

import json
from typing import Callable, Awaitable, Any

from app.tools.file_tools import read_file, write_file
from app.tools.command_tools import execute_command
from app.tools.search_tools import search_code
from app.tools.http_tools import http_request, fetch_webpage
from app.tools.calculator import calculate

# 工具名称到执行函数的映射
TOOL_EXECUTORS: dict[str, Callable[[dict], Awaitable[str]]] = {
    "read_file": read_file,
    "write_file": write_file,
    "execute_command": execute_command,
    "search_code": search_code,
    "http_request": http_request,
    "fetch_webpage": fetch_webpage,
    "calculate": calculate,
}


from app.tools.registry import _TOOL_REGISTRY


def get_tool_executor(tool_name: str) -> Callable[[dict], Awaitable[str]] | None:
    """获取工具执行函数"""
    # 1. 优先从注册表中获取原始函数（针对使用了 @register_tool 的工具）
    if tool_name in _TOOL_REGISTRY:
        return _TOOL_REGISTRY[tool_name].original_func

    # 2. 回退到手动映射
    return TOOL_EXECUTORS.get(tool_name)


def get_all_tools_for_agent(agent) -> list[dict]:
    """获取 Agent 可用的所有工具定义（Claude API 格式）"""
    tools = []
    for tool in agent.tools:
        schema = (
            json.loads(tool.schema) if isinstance(tool.schema, str) else tool.schema
        )
        tools.append(
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": schema,
            }
        )
    return tools


__all__ = [
    "get_tool_executor",
    "get_all_tools_for_agent",
    "read_file",
    "write_file",
    "execute_command",
    "search_code",
    "http_request",
    "fetch_webpage",
]
