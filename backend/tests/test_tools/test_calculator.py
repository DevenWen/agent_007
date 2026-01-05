"""Calculator Tool 单元测试"""

import pytest


@pytest.mark.unit
class TestCalculator:
    """测试 Calculator 工具"""

    async def test_simple_calculation(self):
        """测试简单计算"""
        from app.tools.registry import get_all_registered_tools

        tools = get_all_registered_tools()
        calculate = tools["calculate"].original_func

        result = await calculate({"expression": "2 + 2"})
        assert "Result" in result
        assert "4" in result

    async def test_mathematical_functions(self):
        """测试数学函数"""
        from app.tools.registry import get_all_registered_tools

        tools = get_all_registered_tools()
        calculate = tools["calculate"].original_func

        # 测试 sqrt
        result = await calculate({"expression": "sqrt(16)"})
        assert "4" in result

    async def test_safe_functions_only(self):
        """测试只允许安全函数"""
        from app.tools.registry import get_all_registered_tools

        tools = get_all_registered_tools()
        calculate = tools["calculate"].original_func

        # 测试不允许的函数
        result = await calculate({"expression": "import os"})
        assert "Error" in result

    async def test_division_by_zero(self):
        """测试除零错误"""
        from app.tools.registry import get_all_registered_tools

        tools = get_all_registered_tools()
        calculate = tools["calculate"].original_func

        result = await calculate({"expression": "1 / 0"})
        assert "Error" in result
        assert "Division by zero" in result

    async def test_empty_expression(self):
        """测试空表达式"""
        from app.tools.registry import get_all_registered_tools

        tools = get_all_registered_tools()
        calculate = tools["calculate"].original_func

        result = await calculate({})
        assert "Error" in result
        assert "required" in result

    async def test_complex_expression(self):
        """测试复杂表达式"""
        from app.tools.registry import get_all_registered_tools

        tools = get_all_registered_tools()
        calculate = tools["calculate"].original_func

        result = await calculate({"expression": "2 * (3 + 4) - 5"})
        assert "9" in result
