"""Agent Schemas 单元测试"""

import pytest
from datetime import datetime

from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
)


@pytest.mark.unit
class TestAgentSchemas:
    """测试 Agent Schemas"""

    def test_create_agent_request(self):
        """测试 AgentCreate schema"""
        request = AgentCreate(
            name="Test Agent",
            description="A test agent",
            prompt="You are a helpful assistant",
            params_schema='{"type": "object"}',
            skill_name="data_analyst",
            tool_names=["tool1", "tool2"],
        )
        assert request.name == "Test Agent"
        assert len(request.tool_names) == 2

    def test_create_agent_request_minimal(self):
        """测试 AgentCreate 最小字段"""
        request = AgentCreate(
            name="Test Agent",
            prompt="Test prompt",
        )
        assert request.name == "Test Agent"
        assert request.description is None
        assert request.tool_names is None

    def test_update_agent_request(self):
        """测试 AgentUpdate schema"""
        request = AgentUpdate(
            name="Updated Agent",
            description="Updated description",
        )
        assert request.name == "Updated Agent"
        assert request.description == "Updated description"

    def test_agent_response(self):
        """测试 AgentResponse schema"""
        now = datetime.utcnow()
        response = AgentResponse(
            id="agent-123",
            name="Test Agent",
            description="Test description",
            prompt="Test prompt",
            params_schema=None,
            tool_names=["tool1"],
            created_at=now,
            updated_at=now,
        )
        assert response.id == "agent-123"
        assert len(response.tool_names) == 1

    def test_agent_response_with_skill(self):
        """测试 AgentResponse with skill_name"""
        now = datetime.utcnow()
        response = AgentResponse(
            id="agent-123",
            name="Test Agent",
            prompt="Test prompt",
            skill_name="code_reviewer",
            max_iterations=20,
            created_at=now,
            updated_at=now,
        )
        assert response.skill_name == "code_reviewer"
        assert response.max_iterations == 20
