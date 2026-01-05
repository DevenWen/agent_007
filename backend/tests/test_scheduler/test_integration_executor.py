"""Executor 集成测试

测试目标：
1. 验证 Agent 完整执行流程
2. 实际调用 Anthropic API（需要 ANTHROPIC_API_KEY）
3. 验证工具调用链（Agent -> Executor -> Claude -> Tool -> Result -> Claude -> Answer）
4. 验证结果持久化

注意：此测试需要设置 ANTHROPIC_API_KEY 环境变量。
如果没有设置，测试将被跳过。
"""

import pytest
import os
import json
import logging
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# 确保 calculator 工具被加载
import app.tools.calculator
from app.scheduler.executor import AnthropicExecutor
from app.models.agent import Agent
from app.models.ticket import Ticket, TicketStatus
from app.models.session import Session, SessionStatus
from app.models.tool import Tool

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_integration_flow(db_session, test_engine):
    """
    测试 Agent 完整集成流程：
    1. 创建具备计算能力的 Agent
    2. 提交一个需要计算的任务
    3. 执行并等待完成
    4. 验证结果
    """

    # 0. 检查 API Key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "test_key":
        pytest.skip(
            "Skiping integration test: ANTHROPIC_API_KEY not set or is test_key"
        )

    logger.info("Starting integration test with Analysis Agent...")

    # 1. 准备数据

    # 1.1 创建 Calculator Tool (数据库记录)
    # schema 必须匹配 register_tool 中的定义
    calc_tool = Tool(
        id="tool-calc-001",
        name="calculate",
        description="执行数学计算",
        schema=json.dumps(
            {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            }
        ),
    )
    db_session.add(calc_tool)

    # 1.2 创建 Agent
    agent = Agent(
        id="agent-math-001",
        name="Math Genius",
        description="A math expert who can calculate anything.",
        prompt="You are a helpful math assistant. You MUST use the 'calculate' tool for ANY math calculation, do not calculate in your head. When you have the final answer, you MUST use the 'complete_task' tool to finish the task.",
    )
    agent.tools.append(calc_tool)
    db_session.add(agent)

    # 1.3 创建 Ticket (任务)
    # 任务：计算 15 * 7 + 5，这是一个多步计算或者可以通过一次 eval 完成的任务
    ticket = Ticket(
        id="ticket-integration-001",
        # title="Integration Test Calculation",  <-- Removed
        # content="...", <-- Removed
        # requestor_id="...", <-- Removed
        agent_id=agent.id,
        status=TicketStatus.PENDING.value,
    )
    db_session.add(ticket)

    # 1.4 创建 Session 和初始消息
    session = Session(
        id="session-integration-001",
        ticket_id=ticket.id,
        status=SessionStatus.ACTIVE.value,
    )
    db_session.add(session)

    # 添加用户消息
    from app.models.message import Message, MessageRole

    user_msg = Message(
        session_id=session.id,
        role=MessageRole.USER.value,
        content="Please calculate 12345 * 6789 + 54321 and tell me the result.",
        timestamp=datetime.utcnow(),
    )
    db_session.add(user_msg)

    await db_session.commit()

    # 2. 执行任务

    # Patch executor.async_session_maker 以使用我们的测试数据库 session
    # 我们需要模拟 async_session_maker() 返回一个 context manager，该 manager yield 我们的 db_session

    class MockSessionContext:
        def __init__(self, session):
            self.session = session

        async def __aenter__(self):
            return self.session

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    mock_maker = MagicMock(return_value=MockSessionContext(db_session))

    logger.info("Initializing Executor...")

    with patch("app.scheduler.executor.async_session_maker", mock_maker):
        executor = AnthropicExecutor(ticket.id, session.id)

        logger.info("Running Executor (Turn 1)...")
        await executor.run()

        # 重新加载 ticket 状态
        await db_session.refresh(ticket)
        if ticket.status != TicketStatus.COMPLETED.value:
            logger.info(
                "Agent did not complete task in first turn. Sending follow-up..."
            )
            # 添加跟进消息
            followup_msg = Message(
                session_id=session.id,
                role=MessageRole.USER.value,
                content="I see the result. Please use the complete_task tool to mark this task as done with a summary.",
                timestamp=datetime.utcnow(),
            )
            db_session.add(followup_msg)
            await db_session.commit()

            # 手动追加到 session.messages (因为 executor 是新建的或者需要刷新)
            # 注意：真实的 executor 会从 DB 加载消息，但这里我们重用 executor 对象吗？
            # executor._load_session 会重新加载，所以只需提交 DB。
            # 但 executor 实例如果在内存中维护了 messages，可能需要刷新。
            # 安全起见，我们重新实例化 executor 或确信 run() 会重新加载。
            # 查看 executor.run(): 它调用 self._load_session()。

            logger.info("Running Executor (Turn 2)...")
            # 重新实例化以模拟完整流程（可选，但更稳健）
            executor = AnthropicExecutor(ticket.id, session.id)
            await executor.run()

    # 3. 验证结果

    # 重新加载状态
    await db_session.refresh(ticket)
    await db_session.refresh(session, ["messages"])

    logger.info(f"Task finished with status: {ticket.status}")
    if ticket.error_message:
        logger.error(f"Error message: {ticket.error_message}")

    # 验证所有的消息交互
    logger.info("=== Conversation History ===")
    for msg in sorted(session.messages, key=lambda m: m.timestamp):
        logger.info(f"[{msg.role}] {msg.content}")

    # 断言

    # 3.1 任务应该完成
    assert ticket.status == TicketStatus.COMPLETED.value, (
        f"Ticket failed: {ticket.error_message}"
    )
    assert session.status == SessionStatus.COMPLETED.value

    # 3.2 应该有计算结果 (12345 * 6789 + 54321 = 83810205 + 54321 = 83864526)
    EXPECTED_RESULT = "83864526"

    # 检查最后的 Assistant 消息或 Tool 结果
    last_msg = sorted(session.messages, key=lambda m: m.timestamp)[-1]
    # last_msg might be tool result if complete_task was called last

    # 检查内容中包含结果
    found_result = False
    for msg in session.messages:
        if EXPECTED_RESULT in msg.content or EXPECTED_RESULT in str(msg.content):
            found_result = True
            break

    assert found_result, (
        f"The result '{EXPECTED_RESULT}' was not found in any message content"
    )

    # 3.3 应该调用了 calculate 工具
    tool_calls = [m for m in session.messages if m.role == "tool"]
    assert len(tool_calls) > 0, "No tool calls found"

    has_calc_call = any(
        EXPECTED_RESULT in str(m.content) or "Result" in str(m.content)
        for m in tool_calls
    )
    assert has_calc_call, "Did not find successful calculator execution"

    logger.info("Integration test passed successfully!")
