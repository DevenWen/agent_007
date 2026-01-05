"""文件操作工具"""

import os
from pathlib import Path
from typing import Any
from app.tools.registry import register_tool


@register_tool(name="read_file", description="读取文件内容", input_schema={"path": str})
async def read_file(params: dict[str, Any]) -> str:
    """读取文件内容

    Args:
        params: {"path": "文件路径"}

    Returns:
        文件内容或错误信息
    """
    path = params.get("path", "")
    if not path:
        return "Error: 'path' parameter is required"

    try:
        file_path = Path(path)
        if not file_path.exists():
            return f"Error: File not found: {path}"

        if not file_path.is_file():
            return f"Error: Not a file: {path}"

        # 限制文件大小（1MB）
        if file_path.stat().st_size > 1024 * 1024:
            return f"Error: File too large (max 1MB): {path}"

        content = file_path.read_text(encoding="utf-8")
        return content

    except UnicodeDecodeError:
        return f"Error: Cannot read binary file as text: {path}"
    except PermissionError:
        return f"Error: Permission denied: {path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@register_tool(
    name="write_file",
    description="写入文件内容",
    input_schema={"path": str, "content": str},
)
async def write_file(params: dict[str, Any]) -> str:
    """写入文件内容

    Args:
        params: {"path": "文件路径", "content": "文件内容"}

    Returns:
        成功或错误信息
    """
    path = params.get("path", "")
    content = params.get("content", "")

    if not path:
        return "Error: 'path' parameter is required"

    try:
        file_path = Path(path)

        # 创建父目录（如果不存在）
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} bytes to {path}"

    except PermissionError:
        return f"Error: Permission denied: {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"
