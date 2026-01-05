"""Executor 单元测试

测试目标：
1. 测试 executor 的基本功能
2. 重点测试 tools 调用功能
3. 验证系统工具和普通工具的调用
"""

import pytest
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from app.scheduler.executor import AnthropicExecutor, SYSTEM_TOOLS


@pytest.mark.asyncio
class TestAnthropicExecutor:
    """测试 AnthropicExecutor"""

    def test_executor_init(self):
        """测试 executor 初始化"""
        executor = AnthropicExecutor("ticket-123", "session-123")
        assert executor.ticket_id == "ticket-123"
        assert executor.session_id == "session-123"
        assert executor._should_stop is False

    def test_executor_stop(self):
        """测试 executor 停止功能"""
        executor = AnthropicExecutor("ticket-123", "session-123")
        executor.stop()
        assert executor._should_stop is True

    async def test_load_ticket(self, db_session, sample_ticket):
        """测试加载 Ticket"""
        executor = AnthropicExecutor(sample_ticket.id, "session-123")

        # 重新加载 ticket 以确保有 agent 关系
        await db_session.refresh(sample_ticket, ["agent", "steps"])

        ticket = await executor._load_ticket(db_session)
        assert ticket is not None
        assert ticket.id == sample_ticket.id

    async def test_load_session(self, db_session, sample_session):
        """测试加载 Session"""
        executor = AnthropicExecutor("ticket-123", sample_session.id)

        session = await executor._load_session(db_session)
        assert session is not None
        assert session.id == sample_session.id

    async def test_execute_tool_calculator(self):
        """测试执行 calculator 工具"""
        executor = AnthropicExecutor("ticket-123", "session-123")

        # calculator 工具应该已经注册
        result = await executor._execute_tool("calculate", {"expression": "2 + 2"})

        assert "4" in result
        assert "Result" in result

    async def test_execute_tool_not_found(self):
        """测试执行不存在的工具"""
        executor = AnthropicExecutor("ticket-123", "session-123")

        result = await executor._execute_tool("nonexistent_tool", {})

        assert "not found" in result.lower()

    async def test_handle_system_tool_complete_task(
        self, db_session, sample_ticket, sample_session
    ):
        """测试处理 complete_task 系统工具"""
        from app.models.ticket import TicketStatus
        from app.models.session import SessionStatus

        executor = AnthropicExecutor(sample_ticket.id, sample_session.id)

        result = await executor._handle_system_tool(
            db_session,
            sample_ticket,
            sample_session,
            "complete_task",
            {"summary": "Task done"},
        )

        assert "完成" in result
        assert sample_ticket.status == TicketStatus.COMPLETED.value
        assert sample_session.status == SessionStatus.COMPLETED.value
        assert executor._should_stop is True

    async def test_handle_system_tool_fail_task(
        self, db_session, sample_ticket, sample_session
    ):
        """测试处理 fail_task 系统工具"""
        from app.models.ticket import TicketStatus
        from app.models.session import SessionStatus

        executor = AnthropicExecutor(sample_ticket.id, sample_session.id)

        result = await executor._handle_system_tool(
            db_session,
            sample_ticket,
            sample_session,
            "fail_task",
            {"error": "Test error"},
        )

        assert "失败" in result
        assert sample_ticket.status == TicketStatus.FAILED.value
        assert sample_ticket.error_message == "Test error"
        assert sample_session.status == SessionStatus.FAILED.value
        assert executor._should_stop is True

    async def test_handle_system_tool_suspend(
        self, db_session, sample_ticket, sample_session
    ):
        """测试处理 request_human_input 系统工具"""
        from app.models.ticket import TicketStatus
        from app.models.session import SessionStatus

        executor = AnthropicExecutor(sample_ticket.id, sample_session.id)

        result = await executor._handle_system_tool(
            db_session,
            sample_ticket,
            sample_session,
            "request_human_input",
            {"prompt": "Need input"},
        )

        assert "挂起" in result
        assert sample_ticket.status == TicketStatus.SUSPENDED.value
        assert sample_session.status == SessionStatus.SUSPENDED.value
        assert executor._should_stop is True

    async def test_handle_system_tool_add_step(
        self, db_session, sample_ticket, sample_session
    ):
        """测试处理 add_step 系统工具"""
        from app.models.step import StepStatus

        # 预加载 steps 以避免 lazy loading 问题
        await db_session.refresh(sample_ticket, ["steps"])

        executor = AnthropicExecutor(sample_ticket.id, sample_session.id)

        initial_step_count = len(sample_ticket.steps)

        result = await executor._handle_system_tool(
            db_session,
            sample_ticket,
            sample_session,
            "add_step",
            {"title": "Test Step", "status": "completed"},
        )

        assert "已添加" in result
        assert len(sample_ticket.steps) == initial_step_count + 1
        assert sample_ticket.steps[-1].title == "Test Step"


@pytest.mark.asyncio
class TestSystemTools:
    """测试系统工具定义"""

    def test_system_tools_defined(self):
        """测试系统工具是否正确定义"""
        assert len(SYSTEM_TOOLS) == 4

        tool_names = [t["name"] for t in SYSTEM_TOOLS]
        assert "request_human_input" in tool_names
        assert "complete_task" in tool_names
        assert "fail_task" in tool_names
        assert "add_step" in tool_names

    def test_system_tool_schemas(self):
        """测试系统工具的 schema"""
        for tool in SYSTEM_TOOLS:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert tool["input_schema"]["type"] == "object"
            assert "properties" in tool["input_schema"]
            assert "required" in tool["input_schema"]
