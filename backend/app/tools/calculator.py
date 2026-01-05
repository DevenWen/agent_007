import math
from typing import Any
from app.tools.registry import register_tool

# 允许的安全函数
SAFE_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "pi": math.pi,
    "e": math.e,
}


@register_tool(
    name="calculate", description="执行数学计算", input_schema={"expression": str}
)
async def calculate(params: dict[str, Any]) -> str:
    """执行数学计算（增强版）"""
    expression = params.get("expression", "")
    if not expression:
        return "Error: 'expression' parameter is required"

    try:
        result = eval(expression, {"__builtins__": {}}, SAFE_FUNCTIONS)
        return f"Result: {expression} = {result}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except NameError as e:
        return f"Error: Unknown function - {e}"
    except Exception as e:
        return f"Error: {str(e)}"
