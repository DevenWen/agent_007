"""Session Model 单元测试"""

import pytest

from app.models.session import Session, SessionStatus


@pytest.mark.unit
class TestSessionModel:
    """测试 Session 模型"""

    async def test_create_session(self, db_session, sample_ticket):
        """测试创建 Session"""
        session = Session(
            id="session-123",
            ticket_id=sample_ticket.id,
            status=SessionStatus.ACTIVE.value,
        )

        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        assert session.id == "session-123"
        assert session.ticket_id == sample_ticket.id
        assert session.status == SessionStatus.ACTIVE.value
        assert session.created_at is not None

    async def test_session_status_enum(self):
        """测试 SessionStatus 枚举"""
        assert SessionStatus.ACTIVE.value == "active"
        assert SessionStatus.SUSPENDED.value == "suspended"
        assert SessionStatus.COMPLETED.value == "completed"
        assert SessionStatus.FAILED.value == "failed"

    async def test_session_repr(self, sample_session):
        """测试 Session __repr__ 方法"""
        repr_str = repr(sample_session)
        assert "Session" in repr_str
        assert sample_session.id[:8] in repr_str
        assert sample_session.status in repr_str

    async def test_session_ticket_relationship(self, db_session, sample_session):
        """测试 Session 与 Ticket 的关系"""
        await db_session.refresh(sample_session, ["ticket"])

        assert sample_session.ticket is not None
        assert sample_session.ticket.id == sample_session.ticket_id

    async def test_session_default_status(self, db_session, sample_ticket):
        """测试 Session 默认状态"""
        session = Session(
            id="session-default",
            ticket_id=sample_ticket.id,
        )

        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        assert session.status == SessionStatus.ACTIVE.value
