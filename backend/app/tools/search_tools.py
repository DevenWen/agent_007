"""代码搜索工具"""

import asyncio
import shutil
from typing import Any
from app.tools.registry import register_tool


@register_tool(
    name="search_code",
    description="搜索代码（使用 ripgrep）",
    input_schema={"pattern": str, "path": str},
)
async def search_code(params: dict[str, Any]) -> str:
    """搜索代码（使用 ripgrep）

    Args:
        params: {"pattern": "搜索模式", "path": "搜索路径（默认当前目录）"}

    Returns:
        搜索结果或错误信息
    """
    pattern = params.get("pattern", "")
    path = params.get("path", ".")

    if not pattern:
        return "Error: 'pattern' parameter is required"

    # 检查 ripgrep 是否可用
    rg_path = shutil.which("rg")
    if not rg_path:
        # 回退到 grep
        return await _search_with_grep(pattern, path)

    try:
        # 使用 ripgrep 搜索
        process = await asyncio.create_subprocess_exec(
            "rg",
            "--line-number",  # 显示行号
            "--no-heading",  # 不显示文件名标题
            "--color",
            "never",  # 不使用颜色
            "--max-count",
            "100",  # 每个文件最多100个匹配
            "--max-filesize",
            "1M",  # 跳过大文件
            pattern,
            path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
        except asyncio.TimeoutError:
            process.kill()
            return "Error: Search timed out after 30 seconds"

        if process.returncode == 1:
            return "No matches found"

        if process.returncode != 0 and stderr:
            return f"Error: {stderr.decode('utf-8', errors='replace')}"

        result = stdout.decode("utf-8", errors="replace")

        # 限制输出长度
        if len(result) > 50 * 1024:
            result = result[: 50 * 1024] + "\n... (results truncated)"

        return result if result.strip() else "No matches found"

    except Exception as e:
        return f"Error searching code: {str(e)}"


async def _search_with_grep(pattern: str, path: str) -> str:
    """使用 grep 作为后备方案"""
    try:
        process = await asyncio.create_subprocess_exec(
            "grep",
            "-rn",  # 递归搜索，显示行号
            "--include=*.py",
            "--include=*.js",
            "--include=*.ts",
            "--include=*.java",
            "--include=*.go",
            "--include=*.rs",
            "--include=*.c",
            "--include=*.cpp",
            "--include=*.h",
            pattern,
            path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)

        if process.returncode == 1:
            return "No matches found"

        result = stdout.decode("utf-8", errors="replace")

        if len(result) > 50 * 1024:
            result = result[: 50 * 1024] + "\n... (results truncated)"

        return result if result.strip() else "No matches found"

    except Exception as e:
        return f"Error with grep fallback: {str(e)}"
