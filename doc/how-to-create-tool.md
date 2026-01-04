# 如何创建自定义 Tool

本文档以添加一个**计算器 Tool** 为例，step by step 介绍如何扩展 Agent Platform 的工具能力。

---

## Tool 架构概述

```
backend/app/tools/
├── __init__.py      # 工具注册
├── file_tools.py    # 文件操作
├── command_tools.py # 命令执行
├── search_tools.py  # 代码搜索
├── http_tools.py    # HTTP 请求
└── calculator.py    # 👈 我们要创建的
```

每个 Tool 需要：
1. **执行函数** - 异步函数，接收参数字典，返回字符串结果
2. **数据库记录** - 在 `seeds.py` 中注册 Tool 的 schema
3. **注册到 Executor** - 在 `__init__.py` 中添加映射

---

## Step 1: 创建 Tool 实现

创建 `backend/app/tools/calculator.py`:

```python
"""计算器工具"""

async def calculate(params: dict) -> str:
    """执行数学计算
    
    Args:
        params: {
            "expression": "数学表达式，如 2 + 3 * 4"
        }
    
    Returns:
        计算结果或错误信息
    """
    expression = params.get("expression", "")
    if not expression:
        return "Error: 'expression' parameter is required"
    
    # 安全检查：只允许数学字符
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expression):
        return f"Error: Invalid characters in expression"
    
    try:
        # 使用 eval 计算（已做安全限制）
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {expression} = {result}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {str(e)}"
```

**命名规范**：
- 文件名: `snake_case.py` (如 `calculator.py`)
- 函数名: `snake_case` (如 `calculate`)
- 参数: 使用 `params: dict` 统一接口

---

## Step 2: 注册到 Tools 包

编辑 `backend/app/tools/__init__.py`:

```python
# 添加导入
from app.tools.calculator import calculate

# 在 TOOL_EXECUTORS 字典中添加
TOOL_EXECUTORS: dict[str, Callable[[dict], Awaitable[str]]] = {
    "read_file": read_file,
    "write_file": write_file,
    # ... 其他工具
    "calculate": calculate,  # 👈 添加这行
}
```

---

## Step 3: 添加数据库记录

编辑 `backend/app/seeds.py`，在 `BUILTIN_TOOLS` 列表中添加:

```python
{
    "id": "tool-calculator",
    "name": "calculate",
    "description": "执行数学计算，支持加减乘除和括号",
    "schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "数学表达式，如 '2 + 3 * 4' 或 '(10 + 5) / 3'"
            }
        },
        "required": ["expression"]
    }
},
```

**Schema 规范** (JSON Schema 格式):
- `type`: 参数类型 (`string`, `number`, `object`, `array`, `boolean`)
- `description`: 参数说明，会展示给 Claude
- `required`: 必填参数列表
- `enum`: 可选，限制可选值

---

## Step 4: 重置数据库

新 Tool 需要重新初始化数据库:

```bash
# 删除旧数据库
rm backend/data/agent_platform.db

# 重启后端
cd backend && uv run uvicorn app.main:app --reload --port 8000
```

---

## Step 5: 分配 Tool 给 Agent

创建或更新 Agent，添加新 Tool:

```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Math Agent",
    "prompt": "你是一个数学助手，使用 calculate 工具进行计算。",
    "tool_ids": ["tool-calculator"]
  }'
```

---

## Step 6: 测试

创建 Ticket 测试:

```bash
AGENT_ID=$(curl -s http://localhost:8000/api/agents | jq -r '.[-1].id')

curl -X POST http://localhost:8000/api/tickets \
  -H "Content-Type: application/json" \
  -d "{
    \"agent_id\": \"$AGENT_ID\",
    \"params\": {\"question\": \"计算 (15 + 25) * 2\"}
  }"
```

---

## 完整示例代码

<details>
<summary>calculator.py 完整代码</summary>

```python
"""计算器工具 - 完整版"""
import math

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


async def calculate(params: dict) -> str:
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
```

</details>

---

## 最佳实践

| 项目 | 建议 |
|-----|------|
| 错误处理 | 始终返回字符串，不要抛出异常 |
| 输入验证 | 检查必填参数，验证类型 |
| 输出格式 | 使用 `Result:` 或 `Error:` 前缀 |
| 安全性 | 限制危险操作，设置超时 |
| 日志 | 使用 `logger.info/error` 记录关键信息 |
