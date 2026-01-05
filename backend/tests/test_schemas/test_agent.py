"""Agent Schemas 单元测试"""

import pytest
from datetime import datetime

from app.schemas.agent import (
    AgentSummary,
    AgentResponse,
    CreateAgentRequest,
    UpdateAgentRequest,
)


@pytest.mark.unit
class TestAgentSchemas:
    """测试 Agent Schemas"""

    def test_create_agent_request(self):
        """测试 CreateAgentRequest schema"""
        request = CreateAgentRequest(
            name="Test Agent",
            description="A test agent",
            prompt="You are a helpful assistant",
            params_schema={"type": "object"},
            tool_ids=["tool1", "tool2"],
        )
        assert request.name == "Test Agent"
        assert len(request.tool_ids) == 2

    def test_create_agent_request_minimal(self):
        """测试 CreateAgentRequest 最小字段"""
        request = CreateAgentRequest(
            name="Test Agent",
            prompt="Test prompt",
        )
        assert request.name == "Test Agent"
        assert request.description is None
        assert request.tool_ids == []

    def test_update_agent_request(self):
        """测试 UpdateAgentRequest schema"""
        request = UpdateAgentRequest(
            name="Updated Agent",
            description="Updated description",
        )
        assert request.name == "Updated Agent"
        assert request.description == "Updated description"

    def test_agent_summary(self):
        """测试 AgentSummary schema"""
        summary = AgentSummary(
            id="agent-123",
            name="Test Agent",
            description="Test description",
        )
        assert summary.id == "agent-123"
        assert summary.name == "Test Agent"

    def test_agent_response(self):
        """测试 AgentResponse schema"""
        now = datetime.utcnow()
        response = AgentResponse(
            id="agent-123",
            name="Test Agent",
            description="Test description",
            prompt="Test prompt",
            params_schema=None,
            tool_ids=["tool1"],
            created_at=now,
            updated_at=now,
        )
        assert response.id == "agent-123"
        assert len(response.tool_ids) == 1

    def test_agent_response_parse_params_schema(self):
        """测试 AgentResponse params_schema 解析"""
        now = datetime.utcnow()
        # 测试从字符串解析
        response = AgentResponse(
            id="agent-123",
            name="Test Agent",
            prompt="Test prompt",
            params_schema='{"type": "object"}',
            tool_ids=[],
            created_at=now,
            updated_at=now,
        )
        assert response.params_schema == {"type": "object"}
