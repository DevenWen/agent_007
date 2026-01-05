"""Ticket Model 单元测试"""

import pytest

from app.models.ticket import Ticket, TicketStatus


@pytest.mark.unit
class TestTicketModel:
    """测试 Ticket 模型"""

    async def test_create_ticket(self, db_session, sample_agent):
        """测试创建 Ticket"""
        ticket = Ticket(
            id="test-ticket-123",
            agent_id=sample_agent.id,
            status=TicketStatus.PENDING.value,
            params='{"key": "value"}',
        )

        db_session.add(ticket)
        await db_session.commit()
        await db_session.refresh(ticket)

        assert ticket.id == "test-ticket-123"
        assert ticket.agent_id == sample_agent.id
        assert ticket.status == TicketStatus.PENDING.value
        assert ticket.params == '{"key": "value"}'
        assert ticket.created_at is not None
        assert ticket.updated_at is not None

    async def test_ticket_status_enum(self):
        """测试 TicketStatus 枚举"""
        assert TicketStatus.PENDING.value == "pending"
        assert TicketStatus.RUNNING.value == "running"
        assert TicketStatus.SUSPENDED.value == "suspended"
        assert TicketStatus.COMPLETED.value == "completed"
        assert TicketStatus.FAILED.value == "failed"

    async def test_ticket_repr(self, db_session, sample_ticket):
        """测试 Ticket __repr__ 方法"""
        repr_str = repr(sample_ticket)
        assert "Ticket" in repr_str
        assert sample_ticket.id[:8] in repr_str
        assert sample_ticket.status in repr_str

    async def test_ticket_relationships(self, db_session, sample_ticket):
        """测试 Ticket 与 Agent 的关系"""
        await db_session.refresh(sample_ticket, ["agent"])

        assert sample_ticket.agent is not None
        assert sample_ticket.agent.id == sample_ticket.agent_id
        assert sample_ticket.agent.name == "Test Agent"

    async def test_ticket_default_status(self, db_session, sample_agent):
        """测试 Ticket 默认状态"""
        ticket = Ticket(
            id="test-ticket-default",
            agent_id=sample_agent.id,
        )

        db_session.add(ticket)
        await db_session.commit()
        await db_session.refresh(ticket)

        assert ticket.status == TicketStatus.PENDING.value

    async def test_ticket_with_context(self, db_session, sample_agent):
        """测试带 context 的 Ticket"""
        ticket = Ticket(
            id="test-ticket-ctx",
            agent_id=sample_agent.id,
            status=TicketStatus.PENDING.value,
            context='{"user": "test_user"}',
        )

        db_session.add(ticket)
        await db_session.commit()
        await db_session.refresh(ticket)

        assert ticket.context == '{"user": "test_user"}'

    async def test_ticket_with_error_message(self, db_session, sample_agent):
        """测试带错误信息的 Ticket"""
        ticket = Ticket(
            id="test-ticket-error",
            agent_id=sample_agent.id,
            status=TicketStatus.FAILED.value,
            error_message="Test error message",
        )

        db_session.add(ticket)
        await db_session.commit()
        await db_session.refresh(ticket)

        assert ticket.error_message == "Test error message"
        assert ticket.status == TicketStatus.FAILED.value
