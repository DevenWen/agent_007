"""Dispatcher - 主循环调度器

职责：
1. 定时轮询 pending 状态的 Tickets
2. 为每个 Ticket 创建 Session（如果不存在）
3. 派发给 Executor 执行
"""

import asyncio
import logging
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session_maker
from app.models.ticket import Ticket, TicketStatus
from app.models.session import Session, SessionStatus
from app.config import SCHEDULER_INTERVAL
from app.scheduler.executor_factory import ExecutorFactory

logger = logging.getLogger(__name__)


class Dispatcher:
    """主循环调度器"""

    def __init__(self, interval: float = SCHEDULER_INTERVAL):
        self.interval = interval
        self.running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("Dispatcher already running")
            return

        self.running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"Dispatcher started with interval {self.interval}s")

    def stop(self):
        """停止调度器"""
        self.running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("Dispatcher stopped")

    async def _run_loop(self):
        """主循环"""
        while self.running:
            try:
                await self._dispatch_pending_tickets()
            except Exception as e:
                logger.error(f"Error in dispatcher loop: {e}", exc_info=True)

            await asyncio.sleep(self.interval)

    async def _dispatch_pending_tickets(self):
        """查找并派发 pending 状态的 Tickets"""
        async with async_session_maker() as db:
            # 查找所有 pending 状态的 Tickets
            result = await db.execute(
                select(Ticket)
                .options(
                    selectinload(Ticket.agent),
                    selectinload(Ticket.sessions),
                )
                .where(Ticket.status == TicketStatus.PENDING.value)
            )
            pending_tickets = result.scalars().all()

            for ticket in pending_tickets:
                await self._dispatch_ticket(db, ticket)

            await db.commit()

    async def _dispatch_ticket(self, db, ticket: Ticket):
        """派发单个 Ticket"""
        logger.info(f"Dispatching ticket {ticket.id[:8]}")

        # 更新 Ticket 状态为 running
        ticket.status = TicketStatus.RUNNING.value
        ticket.updated_at = datetime.utcnow()

        # 检查是否有活跃的 Session，没有则创建
        active_session = next(
            (s for s in ticket.sessions if s.status == SessionStatus.ACTIVE.value), None
        )

        if not active_session:
            # 创建新 Session
            active_session = Session(
                id=str(uuid.uuid4()),
                ticket_id=ticket.id,
                status=SessionStatus.ACTIVE.value,
            )
            db.add(active_session)
            logger.info(
                f"Created new session {active_session.id[:8]} for ticket {ticket.id[:8]}"
            )

        await db.flush()

        # 启动 Executor 执行任务（异步）
        # 使用 Factory 创建
        executor = ExecutorFactory.create_executor(ticket.id, active_session.id)
        asyncio.create_task(executor.run())
