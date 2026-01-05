"""Ticket Schemas 单元测试"""

import pytest
from datetime import datetime

from app.schemas.ticket import (
    TicketSummary,
    TicketResponse,
    CreateTicketRequest,
    StepResponse,
    SessionSummary,
)
from app.models.ticket import TicketStatus
from app.models.step import StepStatus
from app.models.session import SessionStatus


@pytest.mark.unit
class TestTicketSchemas:
    """测试 Ticket Schemas"""

    def test_create_ticket_request(self):
        """测试 CreateTicketRequest schema"""
        request = CreateTicketRequest(
            agent_id="agent-123",
            params={"key": "value"},
            context={"ctx": "test"},
        )
        assert request.agent_id == "agent-123"
        assert request.params == {"key": "value"}
        assert request.context == {"ctx": "test"}

    def test_create_ticket_request_minimal(self):
        """测试 CreateTicketRequest 最小字段"""
        request = CreateTicketRequest(agent_id="agent-123")
        assert request.agent_id == "agent-123"
        assert request.params is None
        assert request.context is None

    def test_ticket_summary(self):
        """测试 TicketSummary schema"""
        summary = TicketSummary(
            id="ticket-123",
            agent_id="agent-123",
            agent_name="Test Agent",
            status=TicketStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert summary.id == "ticket-123"
        assert summary.status == TicketStatus.PENDING

    def test_step_response(self):
        """测试 StepResponse schema"""
        now = datetime.utcnow()
        step = StepResponse(
            idx=1,
            title="Step 1",
            status=StepStatus.COMPLETED,
            result={"data": "result"},
            created_at=now,
            updated_at=now,
        )
        assert step.index == 1  # 使用 alias
        assert step.title == "Step 1"

    def test_session_summary(self):
        """测试 SessionSummary schema"""
        session = SessionSummary(
            id="session-123",
            status=SessionStatus.ACTIVE,
            created_at=datetime.utcnow(),
        )
        assert session.id == "session-123"
        assert session.status == SessionStatus.ACTIVE

    def test_ticket_response(self):
        """测试 TicketResponse schema"""
        now = datetime.utcnow()
        response = TicketResponse(
            id="ticket-123",
            agent_id="agent-123",
            agent_name="Test Agent",
            status=TicketStatus.RUNNING,
            params={"key": "value"},
            context={"ctx": "test"},
            error_message=None,
            steps=[],
            sessions=[],
            current_session_id="session-123",
            created_at=now,
            updated_at=now,
        )
        assert response.id == "ticket-123"
        assert response.agent_name == "Test Agent"
        assert len(response.steps) == 0
