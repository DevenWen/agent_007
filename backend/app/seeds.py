"""初始化种子数据"""

import json


# 内置 Tools 定义
BUILTIN_TOOLS = [
    {
        "id": "tool-read-file",
        "name": "read_file",
        "description": "读取文件内容",
        "schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "文件路径"}},
            "required": ["path"],
        },
    },
    {
        "id": "tool-write-file",
        "name": "write_file",
        "description": "写入文件内容",
        "schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "content": {"type": "string", "description": "文件内容"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "id": "tool-exec-cmd",
        "name": "execute_command",
        "description": "执行 shell 命令",
        "schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "要执行的命令"}
            },
            "required": ["command"],
        },
    },
    {
        "id": "tool-search-code",
        "name": "search_code",
        "description": "搜索代码（基于 ripgrep）",
        "schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "搜索模式"},
                "path": {"type": "string", "description": "搜索路径", "default": "."},
            },
            "required": ["pattern"],
        },
    },
    {
        "id": "tool-http-req",
        "name": "http_request",
        "description": "发送 HTTP 请求",
        "schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "请求 URL"},
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE"],
                    "default": "GET",
                },
                "headers": {"type": "object", "description": "请求头"},
                "body": {"type": "string", "description": "请求体"},
            },
            "required": ["url"],
        },
    },
    {
        "id": "tool-fetch-web",
        "name": "fetch_webpage",
        "description": "抓取网页内容",
        "schema": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "网页 URL"}},
            "required": ["url"],
        },
    },
    {
        "id": "tool-calculator",
        "name": "calculate",
        "description": "执行数学计算，支持加减乘除和括号",
        "schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 '2 + 3 * 4' 或 '(10 + 5) / 3'",
                }
            },
            "required": ["expression"],
        },
    },
]


async def seed_tools(db):
    """初始化内置 Tools"""
    from app.models.tool import Tool
    from sqlalchemy import select

    for tool_data in BUILTIN_TOOLS:
        # 检查是否已存在
        result = await db.execute(select(Tool).where(Tool.id == tool_data["id"]))
        if result.scalar_one_or_none():
            continue

        tool = Tool(
            id=tool_data["id"],
            name=tool_data["name"],
            description=tool_data["description"],
            schema=json.dumps(tool_data["schema"]),
        )
        db.add(tool)

    await db.commit()
