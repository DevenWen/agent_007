"""Agent Model 单元测试"""

import pytest
import json

from app.models.agent import Agent


@pytest.mark.unit
class TestAgentModel:
    """测试 Agent 模型"""

    async def test_create_agent(self, db_session):
        """测试创建 Agent"""
        agent = Agent(
            id="agent-123",
            name="Test Agent",
            description="A test agent",
            prompt="You are a test assistant",
        )

        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)

        assert agent.id == "agent-123"
        assert agent.name == "Test Agent"
        assert agent.description == "A test agent"
        assert agent.prompt == "You are a test assistant"
        assert agent.created_at is not None

    async def test_agent_repr(self, sample_agent):
        """测试 Agent __repr__ 方法"""
        repr_str = repr(sample_agent)
        assert "Agent" in repr_str
        assert sample_agent.id in repr_str
        assert sample_agent.name in repr_str

    async def test_agent_with_tools_relationship(
        self, db_session, sample_agent, sample_tool
    ):
        """测试 Agent 与 Tools 的多对多关系"""
        # 将 tool 添加到 agent 的 tools 列表
        await db_session.refresh(sample_agent, ["tools"])
        await db_session.refresh(sample_tool)

        sample_agent.tools.append(sample_tool)
        await db_session.commit()

        # 重新加载 agent 并验证关系
        await db_session.refresh(sample_agent, ["tools"])

        assert len(sample_agent.tools) == 1
        assert sample_agent.tools[0].name == sample_tool.name

    async def test_agent_minimal_fields(self, db_session):
        """测试 Agent 最小必需字段"""
        agent = Agent(
            id="agent-minimal",
            name="Minimal Agent",
            prompt="Minimal prompt",
        )

        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)

        assert agent.id == "agent-minimal"
        assert agent.description is None  # 可选字段

    # PRD 0.0.3: Skill System 相关测试
    async def test_agent_with_skill_name(self, db_session):
        """测试 Agent 关联 Skill"""
        agent = Agent(
            id="agent-skill",
            name="Skill Agent",
            prompt="Test",
            skill_name="data_analyst",
        )

        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)

        assert agent.skill_name == "data_analyst"

    async def test_agent_max_iterations_default(self, db_session):
        """测试 max_iterations 默认值为 10"""
        agent = Agent(
            id="agent-iter",
            name="Iteration Agent",
            prompt="Test",
        )

        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)

        assert agent.max_iterations == 10

    async def test_agent_with_default_params(self, db_session):
        """测试 Agent 带有 default_params"""
        default_params = {"repo": "github.com/test", "branch": "main"}
        agent = Agent(
            id="agent-params",
            name="Params Agent",
            prompt="Test",
            default_params=json.dumps(default_params),
        )

        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)

        assert agent.default_params is not None
        loaded_params = json.loads(agent.default_params)
        assert loaded_params["repo"] == "github.com/test"
        assert loaded_params["branch"] == "main"

    async def test_agent_with_tool_names(self, db_session):
        """测试 Agent 带有 tool_names"""
        tool_names = ["read_file", "search_code", "http_request"]
        agent = Agent(
            id="agent-tools",
            name="Tools Agent",
            prompt="Test",
            tool_names=json.dumps(tool_names),
        )

        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)

        assert agent.tool_names is not None
        loaded_tools = json.loads(agent.tool_names)
        assert len(loaded_tools) == 3
        assert "read_file" in loaded_tools
