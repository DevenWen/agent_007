"""命令执行工具"""

import asyncio
from typing import Any
from app.tools.registry import register_tool


@register_tool(
    name="execute_command", description="执行 shell 命令", input_schema={"command": str}
)
async def execute_command(params: dict[str, Any]) -> str:
    """执行 shell 命令

    Args:
        params: {"command": "要执行的命令"}

    Returns:
        命令输出或错误信息
    """
    command = params.get("command", "")
    if not command:
        return "Error: 'command' parameter is required"

    # 安全检查：禁止危险命令
    dangerous_patterns = ["rm -rf /", "mkfs", "dd if=", ":(){:|:&};:"]
    for pattern in dangerous_patterns:
        if pattern in command:
            return f"Error: Command contains dangerous pattern: {pattern}"

    try:
        # 使用 asyncio.subprocess 异步执行
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=None,  # 使用当前工作目录
        )

        # 设置超时（60秒）
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60.0)
        except asyncio.TimeoutError:
            process.kill()
            return "Error: Command timed out after 60 seconds"

        # 构建输出
        result_parts = []

        if stdout:
            stdout_text = stdout.decode("utf-8", errors="replace")
            # 限制输出长度（100KB）
            if len(stdout_text) > 100 * 1024:
                stdout_text = stdout_text[: 100 * 1024] + "\n... (output truncated)"
            result_parts.append(f"STDOUT:\n{stdout_text}")

        if stderr:
            stderr_text = stderr.decode("utf-8", errors="replace")
            if len(stderr_text) > 100 * 1024:
                stderr_text = stderr_text[: 100 * 1024] + "\n... (output truncated)"
            result_parts.append(f"STDERR:\n{stderr_text}")

        exit_code = process.returncode
        result_parts.append(f"Exit code: {exit_code}")

        return (
            "\n\n".join(result_parts)
            if result_parts
            else "Command completed with no output"
        )

    except Exception as e:
        return f"Error executing command: {str(e)}"
