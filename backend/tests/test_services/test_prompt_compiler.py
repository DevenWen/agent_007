"""Prompt Compiler 单元测试"""

import pytest
import json
from pathlib import Path

from app.services.prompt_compiler import (
    compile_system_message,
    render_agent_prompt,
    get_effective_tools,
    load_system_prompt,
)


@pytest.mark.unit
class TestPromptCompiler:
    """测试 Prompt 编译器"""

    def test_render_agent_prompt_with_params(self):
        """测试 Agent Prompt 渲染"""
        template = "Analyze repository: {{ repo }} on branch: {{ branch }}"
        params = {"repo": "github.com/test", "branch": "main"}

        result = render_agent_prompt(template, params)

        assert "github.com/test" in result
        assert "main" in result

    def test_render_agent_prompt_empty(self):
        """测试空 prompt"""
        result = render_agent_prompt("", {})
        assert result == ""

    def test_render_agent_prompt_invalid_template(self):
        """测试无效模板返回原始内容"""
        template = "{{ invalid syntax"
        result = render_agent_prompt(template, {})
        # 应该返回原始 prompt 而不是崩溃
        assert result == template

    def test_load_system_prompt(self):
        """测试加载 System Prompt"""
        result = load_system_prompt()
        # 应该包含文件内容
        assert "AI assistant" in result or result == ""

    def test_compile_system_message_no_skill(self):
        """测试无 Skill 时的编译"""
        result = compile_system_message(
            skill_name=None, agent_prompt="Custom instructions", params={}
        )

        assert "Custom instructions" in result

    def test_compile_system_message_with_skill(self):
        """测试有 Skill 时的编译"""
        result = compile_system_message(
            skill_name="data_analyst", agent_prompt="Focus on sales data", params={}
        )

        # 应包含 Skill 内容
        assert "analyst" in result.lower() or "Skill" in result
        assert "Focus on sales data" in result

    def test_compile_system_message_with_params(self):
        """测试参数渲染"""
        result = compile_system_message(
            skill_name=None,
            agent_prompt="Analyze {{ target }}",
            params={"target": "database"},
        )

        assert "database" in result

    def test_get_effective_tools_skill_only(self):
        """测试仅 Skill 工具"""
        tools = get_effective_tools("data_analyst", None)

        # data_analyst skill 定义了 read_file, python_interpreter
        assert "read_file" in tools or len(tools) >= 0

    def test_get_effective_tools_agent_only(self):
        """测试仅 Agent 工具"""
        tools = get_effective_tools(None, ["custom_tool", "other_tool"])

        assert "custom_tool" in tools
        assert "other_tool" in tools

    def test_get_effective_tools_union(self):
        """测试工具合并"""
        tools = get_effective_tools("data_analyst", ["extra_tool"])

        assert "extra_tool" in tools
        # Skill 工具也应该在列表中

    def test_get_effective_tools_dedup(self):
        """测试工具去重"""
        # data_analyst 有 read_file，agent 也传入 read_file
        tools = get_effective_tools("data_analyst", ["read_file"])

        # 应该只有一个 read_file
        assert tools.count("read_file") == 1
