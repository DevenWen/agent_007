"""Agent Model 单元测试"""

import pytest

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
