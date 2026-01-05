"""全局测试配置和 Fixtures"""

import os
import sys
import json
from pathlib import Path
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base
from app.models.agent import Agent
from app.models.ticket import Ticket, TicketStatus
from app.models.session import Session, SessionStatus
from app.models.tool import Tool


# ============================================================================
# 数据库 Fixtures
# ============================================================================


@pytest.fixture(scope="function")
async def test_engine():
    """创建测试用的内存数据库引擎"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 清理
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试用的数据库会话"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


# ============================================================================
# 测试数据 Fixtures
# ============================================================================


@pytest.fixture
async def sample_agent(db_session: AsyncSession) -> Agent:
    """创建样例 Agent"""
    agent = Agent(
        id="test-agent-001",
        name="Test Agent",
        description="A test agent for unit tests",
        prompt="You are a helpful test assistant.",
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


@pytest.fixture
async def sample_tool(db_session: AsyncSession) -> Tool:
    """创建样例 Tool"""
    tool = Tool(
        id="test-tool-001",
        name="test_tool",
        description="A test tool",
        schema=json.dumps(
            {
                "type": "object",
                "properties": {"param": {"type": "string"}},
                "required": ["param"],
            }
        ),
    )
    db_session.add(tool)
    await db_session.commit()
    await db_session.refresh(tool)
    return tool


@pytest.fixture
async def sample_ticket(db_session: AsyncSession, sample_agent: Agent) -> Ticket:
    """创建样例 Ticket"""
    ticket = Ticket(
        id="test-ticket-001",
        agent_id=sample_agent.id,
        status=TicketStatus.PENDING.value,
        params='{"task": "test task"}',
        context='{"context": "test context"}',
    )
    db_session.add(ticket)
    await db_session.commit()
    await db_session.refresh(ticket)
    return ticket


@pytest.fixture
async def sample_session(db_session: AsyncSession, sample_ticket: Ticket) -> Session:
    """创建样例 Session"""
    session = Session(
        id="test-session-001",
        ticket_id=sample_ticket.id,
        status=SessionStatus.ACTIVE.value,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session


# ============================================================================
# 环境变量 Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def test_env():
    """设置测试环境变量"""
    # 保存原始环境变量
    original_env = os.environ.copy()

    # 设置测试环境变量
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["API_PREFIX"] = "/api"
    os.environ["SCHEDULER_INTERVAL"] = "1.0"

    yield

    # 恢复原始环境变量
    os.environ.clear()
    os.environ.update(original_env)


# ============================================================================
# Mock Helpers
# ============================================================================


@pytest.fixture
def mock_file_system(tmp_path):
    """Mock 文件系统，使用临时目录"""
    return tmp_path
