import asyncio
from app.tools import get_tool_executor
from app.tools.registry import _TOOL_REGISTRY

# 确保 calculate 被注册
import app.tools.calculator


async def test():
    print(f"Registry keys: {list(_TOOL_REGISTRY.keys())}")

    executor = get_tool_executor("calculate")
    print(f"Executor for calculate: {executor}")
    print(f"Is callable? {callable(executor)}")

    if callable(executor):
        try:
            # 尝试调用
            result = await executor({"expression": "1+1"})
            print(f"Execution result: {result}")
        except Exception as e:
            print(f"Execution failed: {e}")


if __name__ == "__main__":
    asyncio.run(test())
