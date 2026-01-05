"""Registry Tool 单元测试"""

import pytest


@pytest.mark.unit
class TestRegistry:
    """测试工具注册机制"""

    def test_register_tool(self):
        """测试注册工具"""
        from app.tools.registry import register_tool, get_all_registered_tools

        # 创建一个测试工具
        @register_tool(
            name="test_tool_xyz", description="A test tool", input_schema={"param": str}
        )
        async def test_tool(params: dict) -> dict:
            return {"result": "ok"}

        # 验证工具已注册
        all_tools = get_all_registered_tools()
        assert "test_tool_xyz" in all_tools
        assert all_tools["test_tool_xyz"].name == "test_tool_xyz"
        assert all_tools["test_tool_xyz"].description == "A test tool"

    def test_get_sdk_tools_for_agent(self):
        """测试获取 Agent 的 SDK 工具"""
        from app.tools.registry import get_sdk_tools_for_agent, get_all_registered_tools

        # 获取所有已注册工具的名称
        all_tools = get_all_registered_tools()
        tool_names = list(all_tools.keys())[:2]  # 取前两个

        # 获取 SDK 工具
        sdk_tools = get_sdk_tools_for_agent(tool_names)
        assert len(sdk_tools) == len(tool_names)

    def test_convert_to_json_schema(self):
        """测试 schema 转换"""
        from app.tools.registry import _convert_to_json_schema

        # 测试简单类型转换
        schema = _convert_to_json_schema({"name": str, "age": int})
        assert schema["type"] == "object"
        assert "properties" in schema
        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["age"]["type"] == "integer"

    def test_json_schema_passthrough(self):
        """测试 JSON schema 直接透传"""
        from app.tools.registry import _convert_to_json_schema

        # 测试已经是 JSON schema 格式的情况
        json_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        result = _convert_to_json_schema(json_schema)
        assert result == json_schema
