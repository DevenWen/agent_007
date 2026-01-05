"""简化的 Scheduler 基础测试"""

import pytest
from unittest.mock import AsyncMock, Mock, patch


@pytest.mark.unit
class TestDispatcherBasic:
    """测试 Dispatcher 基础功能"""

    def test_dispatcher_init(self):
        """测试 Dispatcher 初始化"""
        from app.scheduler.dispatcher import Dispatcher

        dispatcher = Dispatcher(interval=1.0)
        assert dispatcher.interval == 1.0
        assert dispatcher.running is False

    async def test_dispatcher_start_stop(self):
        """测试 Dispatcher 启动和停止"""
        from app.scheduler.dispatcher import Dispatcher

        dispatcher = Dispatcher(interval=0.1)

        # 测试启动
        await dispatcher.start()
        assert dispatcher.running is True

        # 测试停止
        dispatcher.stop()
        assert dispatcher.running is False

    @patch("app.scheduler.dispatcher.async_session_maker")
    @patch("app.scheduler.dispatcher.ExecutorFactory.create_executor")
    async def test_dispatch_pending_tickets_no_tickets(
        self, mock_factory, mock_session_maker
    ):
        """测试没有pending tickets的情况"""
        from app.scheduler.dispatcher import Dispatcher

        # Mock 数据库会话
        mock_db = AsyncMock()
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        mock_session_maker.return_value.__aenter__.return_value = mock_db

        dispatcher = Dispatcher(interval=0.1)
        await dispatcher._dispatch_pending_tickets()

        # 验证没有创建 executor
        mock_factory.assert_not_called()


@pytest.mark.unit
class TestExecutorFactory:
    """测试 Executor Factory"""

    def test_create_executor(self):
        """测试创建 executor"""
        from app.scheduler.executor_factory import ExecutorFactory

        executor = ExecutorFactory.create_executor("ticket-123", "session-123")
        assert executor is not None
