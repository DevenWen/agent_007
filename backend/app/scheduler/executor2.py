"""SDK Executor - 基于 claude_agent_sdk 的执行器"""

import logging
import json
import asyncio
from typing import Any, List, Dict

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session_maker
from app.models.agent import Agent as DbAgent
from app.models.ticket import Ticket, TicketStatus
from app.models.session import Session, SessionStatus
from app.models.message import Message, MessageRole
from app.models.step import Step, StepStatus
from app.scheduler.base_executor import IExecutor
from app.tools.registry import get_sdk_tools_for_agent
from app.scheduler.context import execution_context, ExecutionContext
from app.tools.system_tools import (
    request_human_input,
    complete_task,
    fail_task,
    add_step,
)

# Direct import since dependency is installed
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, create_sdk_mcp_server
from claude_agent_sdk.types import TextBlock, ToolUseBlock, ResultMessage

logger = logging.getLogger(__name__)


class SDKExecutor(IExecutor):
    """基于 SDK 的执行器"""

    def __init__(self, ticket_id: str, session_id: str):
        self.ticket_id = ticket_id
        self.session_id = session_id
        self._should_stop = False
        self._client = None
        self._stop_event = asyncio.Event()

    def stop(self):
        """标记停止并触发事件"""
        self._should_stop = True
        self._stop_event.set()
        # 创建一个任务来异步断开连接
        if self._client:
            asyncio.create_task(self._disconnect_client())

    async def _disconnect_client(self):
        """异步断开 SDK 客户端连接"""
        if self._client:
            try:
                logger.info("Disconnecting SDK client...")
                await self._client.disconnect()
                logger.info("SDK client disconnected")
            except Exception as e:
                logger.warning(f"Error disconnecting client: {e}")

    async def run(self):
        try:
            async with async_session_maker() as db:
                ticket = await self._load_ticket(db)
                if not ticket:
                    return
                session = await self._load_session(db)
                if not session:
                    return

                agent_def = ticket.agent

                # 0. Set Execution Context
                ctx_token = execution_context.set(
                    ExecutionContext(
                        db=db, ticket=ticket, session=session, executor=self
                    )
                )

                try:
                    # 1. Gather Tools
                    system_tools = [
                        request_human_input,
                        complete_task,
                        fail_task,
                        add_step,
                    ]

                    # Get User Tools
                    tool_names = [t.name for t in agent_def.tools]
                    user_tools = get_sdk_tools_for_agent(tool_names)

                    all_tools = user_tools + system_tools

                    # Create MCP Server
                    logger.debug(f"Creating MCP server with {len(all_tools)} tools")
                    for tool in all_tools:
                        tool_name = getattr(tool, "__name__", str(tool))
                        logger.debug(f"  - Tool: {tool_name}")

                    server = create_sdk_mcp_server("local_tools", tools=all_tools)
                    logger.debug(f"MCP server created: {server}")

                    # 2. Configure Options
                    logger.debug(
                        f"Agent prompt length: {len(agent_def.prompt) if agent_def.prompt else 0}"
                    )
                    options = ClaudeAgentOptions(
                        permission_mode="bypassPermissions",
                        system_prompt=agent_def.prompt,
                        mcp_servers={"local": server},
                    )
                    logger.debug(f"ClaudeAgentOptions created: {options}")

                    # 3. Build Initial Prompt
                    context_str = self._build_context_str(ticket)
                    initial_prompt = f"{context_str}\n\n请开始执行任务。"
                    logger.debug(f"Initial prompt length: {len(initial_prompt)}")
                    logger.debug(f"Initial prompt preview: {initial_prompt[:200]}...")

                    # 4. Initialize Client
                    logger.info("Creating ClaudeSDKClient...")
                    self._client = ClaudeSDKClient(options)
                    logger.info(f"ClaudeSDKClient created: {self._client}")

                    # 5. Connect WITHOUT initial prompt (use streaming mode)
                    # SDK requires streaming mode for bidirectional communication
                    logger.info(f"SDKExecutor connecting for agent {agent_def.name}")
                    logger.info("Calling connect() in streaming mode...")
                    try:
                        await self._client.connect()  # No prompt - streaming mode
                        logger.info("connect() completed successfully")
                    except Exception as conn_err:
                        logger.error(
                            f"connect() failed: {type(conn_err).__name__}: {conn_err}"
                        )
                        logger.error(f"Client state after error: {self._client}")
                        raise

                    # 6. Send initial prompt via query()
                    logger.info("Sending initial prompt via query()...")
                    await self._client.query(initial_prompt)

                    # 7. Message Loop
                    try:
                        async for message in self._client.receive_messages():
                            # Check for ResultMessage (indicates completion)
                            if isinstance(message, ResultMessage):
                                logger.info(
                                    "Received ResultMessage, agent completed response"
                                )
                                break

                            # Save Assistant Messages to DB
                            if hasattr(message, "content"):
                                blocks = []
                                for block in message.content:
                                    if isinstance(block, TextBlock):
                                        blocks.append(
                                            {"type": "text", "text": block.text}
                                        )
                                    elif isinstance(block, ToolUseBlock):
                                        blocks.append(
                                            {
                                                "type": "tool_use",
                                                "id": block.id,
                                                "name": block.name,
                                                "input": block.input,
                                            }
                                        )

                                if blocks:
                                    db_msg = Message(
                                        session_id=session.id,
                                        role=MessageRole.ASSISTANT.value,
                                        content=json.dumps(blocks, ensure_ascii=False),
                                        timestamp=asyncio.get_event_loop().time(),  # Use standard time roughly or datetime
                                    )
                                    # timestamp needs datetime
                                    from datetime import datetime

                                    db_msg.timestamp = datetime.utcnow()

                                    db.add(db_msg)
                                    await db.commit()

                            if self._should_stop:
                                logger.info("Stop flag set, exiting loop")
                                break

                    except Exception as e:
                        logger.error(f"SDK Loop Error: {e}")
                    finally:
                        await self._client.disconnect()
                        await db.commit()

                finally:
                    execution_context.reset(ctx_token)

        except Exception as e:
            logger.error(f"SDKExecutor error: {e}", exc_info=True)
            await self._mark_failed(str(e))

    async def _load_ticket(self, db) -> Ticket | None:
        result = await db.execute(
            select(Ticket)
            .options(
                selectinload(Ticket.agent).selectinload(DbAgent.tools),
                selectinload(Ticket.steps),
            )
            .where(Ticket.id == self.ticket_id)
        )
        return result.scalar_one_or_none()

    async def _load_session(self, db) -> Session | None:
        result = await db.execute(
            select(Session)
            .options(selectinload(Session.messages))
            .where(Session.id == self.session_id)
        )
        return result.scalar_one_or_none()

    def _build_context_str(self, ticket):
        ctx_str = ""
        if ticket.context:
            ctx_str += f"\nContext: {ticket.context}"
        if ticket.params:
            ctx_str += f"\nParams: {ticket.params}"
        return ctx_str

    async def _mark_failed(self, error: str):
        async with async_session_maker() as db:
            result = await db.execute(select(Ticket).where(Ticket.id == self.ticket_id))
            ticket = result.scalar_one_or_none()
            if ticket:
                ticket.status = TicketStatus.FAILED.value
                ticket.error_message = error

            result = await db.execute(
                select(Session).where(Session.id == self.session_id)
            )
            session = result.scalar_one_or_none()
            if session:
                session.status = SessionStatus.FAILED.value

            await db.commit()
