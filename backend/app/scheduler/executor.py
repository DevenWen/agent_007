"""Executor - Agent 任务执行器

职责：
1. 加载 Agent 配置和 Session 上下文
2. 调用 claude_agent_sdk 执行对话
3. 处理 Tool 调用
4. 处理系统工具（人工介入、任务完成、任务失败）
5. 更新 Step 和 Message
"""

import asyncio
import os
import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session_maker
from app.models.agent import Agent
from app.models.ticket import Ticket, TicketStatus
from app.models.session import Session, SessionStatus
from app.models.message import Message, MessageRole
from app.models.step import Step, StepStatus
from app.tools import get_tool_executor, get_all_tools_for_agent
from app.scheduler.base_executor import IExecutor

logger = logging.getLogger(__name__)


# ============================================================
# 系统工具定义
# ============================================================

SYSTEM_TOOLS = [
    {
        "name": "request_human_input",
        "description": "请求人工介入，暂停任务等待用户输入。当你需要用户提供额外信息、确认操作或做出决策时使用此工具。",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "向用户展示的提示信息，说明需要什么输入",
                }
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "complete_task",
        "description": "标记任务完成。当任务目标已达成时调用此工具。",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "任务完成摘要"},
                "result": {"type": "object", "description": "任务结果数据（可选）"},
            },
            "required": ["summary"],
        },
    },
    {
        "name": "fail_task",
        "description": "标记任务失败。当遇到无法恢复的错误时调用此工具。",
        "input_schema": {
            "type": "object",
            "properties": {"error": {"type": "string", "description": "错误描述"}},
            "required": ["error"],
        },
    },
    {
        "name": "add_step",
        "description": "添加一个任务步骤。用于记录任务的子步骤进度。",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "步骤标题"},
                "status": {
                    "type": "string",
                    "enum": ["pending", "running", "completed", "failed"],
                    "description": "步骤状态",
                },
                "result": {"type": "object", "description": "步骤结果（可选）"},
            },
            "required": ["title", "status"],
        },
    },
]


class AnthropicExecutor(IExecutor):
    """Agent 任务执行器 (Anthropic 原生 API 实现)"""

    def __init__(self, ticket_id: str, session_id: str):
        self.ticket_id = ticket_id
        self.session_id = session_id
        self._should_stop = False

    async def run(self):
        """执行任务主循环"""
        try:
            async with async_session_maker() as db:
                # 加载 Ticket, Agent, Session
                ticket = await self._load_ticket(db)
                if not ticket:
                    logger.error(f"Ticket {self.ticket_id} not found")
                    return

                session = await self._load_session(db)
                if not session:
                    logger.error(f"Session {self.session_id} not found")
                    return

                agent = ticket.agent
                logger.info(
                    f"Executor started for ticket {ticket.id[:8]}, agent: {agent.name}"
                )

                # 构建初始消息（如果是新 Session）
                if not session.messages:
                    await self._add_system_message(db, session, agent, ticket)

                # 主执行循环
                await self._execute_loop(db, ticket, session, agent)

                await db.commit()

        except Exception as e:
            logger.error(
                f"Executor error for ticket {self.ticket_id}: {e}", exc_info=True
            )
            await self._mark_failed(str(e))

    def stop(self):
        """停止任务"""
        self._should_stop = True

    async def _load_ticket(self, db) -> Ticket | None:
        """加载 Ticket"""
        result = await db.execute(
            select(Ticket)
            .options(
                selectinload(Ticket.agent).selectinload(Agent.tools),
                selectinload(Ticket.steps),
            )
            .where(Ticket.id == self.ticket_id)
        )
        return result.scalar_one_or_none()

    async def _load_session(self, db) -> Session | None:
        """加载 Session"""
        result = await db.execute(
            select(Session)
            .options(selectinload(Session.messages))
            .where(Session.id == self.session_id)
        )
        return result.scalar_one_or_none()

    async def _add_system_message(
        self, db, session: Session, agent: Agent, ticket: Ticket
    ):
        """添加系统消息"""
        from app.services.prompt_compiler import compile_system_message

        # 构建任务上下文
        context_str = ""
        if ticket.context:
            ctx = (
                json.loads(ticket.context)
                if isinstance(ticket.context, str)
                else ticket.context
            )
            context_str = f"\n\n## 任务上下文\n```json\n{json.dumps(ctx, ensure_ascii=False, indent=2)}\n```"

        # 构建任务参数
        params_str = ""
        params_dict = {}
        if ticket.params:
            params_dict = (
                json.loads(ticket.params)
                if isinstance(ticket.params, str)
                else ticket.params
            )
            params_str = f"\n\n## 任务参数\n```json\n{json.dumps(params_dict, ensure_ascii=False, indent=2)}\n```"

        # 使用 prompt_compiler 编译完整的 system message
        # Merge Strategy: System Prompt + Skill Content + Agent Prompt (rendered with params)
        compiled_prompt = compile_system_message(
            skill_name=agent.skill_name, agent_prompt=agent.prompt, params=params_dict
        )

        system_content = f"{compiled_prompt}{context_str}{params_str}"

        message = Message(
            session_id=session.id,
            role=MessageRole.SYSTEM.value,
            content=system_content,
            timestamp=datetime.utcnow(),
        )
        db.add(message)
        session.messages.append(message)
        await db.flush()

    async def _execute_loop(self, db, ticket: Ticket, session: Session, agent: Agent):
        """执行循环"""
        import anthropic

        # 初始化 Anthropic 客户端
        client = anthropic.Anthropic()

        # 获取 Agent 可用的工具
        logger.info(
            f"Agent {agent.name} has {len(agent.tools)} tools: {[t.name for t in agent.tools]}"
        )
        agent_tools = get_all_tools_for_agent(agent)
        all_tools = agent_tools + SYSTEM_TOOLS
        logger.info(
            f"Total tools for API call: {len(all_tools)} (agent: {len(agent_tools)}, system: {len(SYSTEM_TOOLS)})"
        )

        max_iterations = 50  # 防止无限循环
        iteration = 0

        while not self._should_stop and iteration < max_iterations:
            iteration += 1

            # 构建消息历史
            messages = self._build_messages(session)

            # 调用 Claude API
            try:
                model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
                logger.info(f"Calling Claude API with model: {model}")
                response = client.messages.create(
                    model=model,
                    max_tokens=4096,
                    system=self._get_system_message(session),
                    messages=messages,
                    tools=all_tools,
                )
            except Exception as e:
                logger.error(f"Claude API error: {e}")
                await self._handle_system_tool(
                    db, ticket, session, "fail_task", {"error": str(e)}
                )
                break

            # 处理响应
            await self._handle_response(db, ticket, session, response)

            # 检查是否需要停止
            if response.stop_reason == "end_turn":
                # 没有工具调用，检查是否需要继续
                if not any(block.type == "tool_use" for block in response.content):
                    logger.info("No tool calls, waiting for next input or ending")
                    break

            await db.flush()

        if iteration >= max_iterations:
            logger.warning(f"Max iterations reached for ticket {ticket.id[:8]}")
            await self._handle_system_tool(
                db, ticket, session, "fail_task", {"error": "Max iterations reached"}
            )

    def _get_system_message(self, session: Session) -> str:
        """获取系统消息"""
        for msg in session.messages:
            if msg.role == MessageRole.SYSTEM.value:
                return msg.content
        return ""

    def _build_messages(self, session: Session) -> list:
        """构建 API 消息格式"""
        messages = []
        for msg in sorted(session.messages, key=lambda m: m.timestamp):
            if msg.role == MessageRole.SYSTEM.value:
                continue  # 系统消息单独传

            if msg.role == MessageRole.USER.value:
                messages.append({"role": "user", "content": msg.content})
            elif msg.role == MessageRole.ASSISTANT.value:
                # 尝试解析为 content blocks
                try:
                    content = json.loads(msg.content)
                    if isinstance(content, list):
                        messages.append({"role": "assistant", "content": content})
                    else:
                        messages.append({"role": "assistant", "content": msg.content})
                except json.JSONDecodeError:
                    messages.append({"role": "assistant", "content": msg.content})
            elif msg.role == MessageRole.TOOL.value:
                # 工具结果消息
                try:
                    tool_result = json.loads(msg.content)
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_result.get("tool_use_id", ""),
                                    "content": tool_result.get("result", ""),
                                }
                            ],
                        }
                    )
                except json.JSONDecodeError:
                    pass

        # 如果没有用户消息，添加一个启动消息
        if not messages:
            messages.append({"role": "user", "content": "请开始执行任务。"})

        return messages

    async def _handle_response(self, db, ticket: Ticket, session: Session, response):
        """处理 Claude 响应"""
        # 保存 assistant 消息
        content_blocks = []
        for block in response.content:
            if block.type == "text":
                content_blocks.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                content_blocks.append(
                    {
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    }
                )

        assistant_msg = Message(
            session_id=session.id,
            role=MessageRole.ASSISTANT.value,
            content=json.dumps(content_blocks, ensure_ascii=False),
            timestamp=datetime.utcnow(),
        )
        db.add(assistant_msg)
        session.messages.append(assistant_msg)

        # 处理工具调用
        for block in response.content:
            if block.type == "tool_use":
                await self._handle_tool_call(db, ticket, session, block)

    async def _handle_tool_call(self, db, ticket: Ticket, session: Session, tool_block):
        """处理工具调用"""
        tool_name = tool_block.name
        tool_input = tool_block.input
        tool_id = tool_block.id

        logger.info(f"Tool call: {tool_name}")

        # 检查是否是系统工具
        if tool_name in [
            "request_human_input",
            "complete_task",
            "fail_task",
            "add_step",
        ]:
            result = await self._handle_system_tool(
                db, ticket, session, tool_name, tool_input
            )
        else:
            # 执行普通工具
            result = await self._execute_tool(tool_name, tool_input)

        # 保存工具结果
        tool_msg = Message(
            session_id=session.id,
            role=MessageRole.TOOL.value,
            content=json.dumps(
                {
                    "tool_use_id": tool_id,
                    "tool_name": tool_name,
                    "result": result,
                },
                ensure_ascii=False,
            ),
            timestamp=datetime.utcnow(),
        )
        db.add(tool_msg)
        session.messages.append(tool_msg)

    async def _handle_system_tool(
        self, db, ticket: Ticket, session: Session, tool_name: str, tool_input: dict
    ) -> str:
        """处理系统工具"""
        if tool_name == "request_human_input":
            # 挂起任务等待人工输入
            ticket.status = TicketStatus.SUSPENDED.value
            session.status = SessionStatus.SUSPENDED.value
            self._should_stop = True
            logger.info(f"Ticket {ticket.id[:8]} suspended for human input")
            return f"任务已挂起，等待用户输入。提示: {tool_input.get('prompt', '')}"

        elif tool_name == "complete_task":
            # 完成任务
            ticket.status = TicketStatus.COMPLETED.value
            session.status = SessionStatus.COMPLETED.value
            self._should_stop = True
            logger.info(f"Ticket {ticket.id[:8]} completed")
            return f"任务已完成。摘要: {tool_input.get('summary', '')}"

        elif tool_name == "fail_task":
            # 任务失败
            ticket.status = TicketStatus.FAILED.value
            ticket.error_message = tool_input.get("error", "Unknown error")
            session.status = SessionStatus.FAILED.value
            self._should_stop = True
            logger.info(f"Ticket {ticket.id[:8]} failed: {ticket.error_message}")
            return f"任务已标记为失败。错误: {ticket.error_message}"

        elif tool_name == "add_step":
            # 添加步骤
            step_idx = len(ticket.steps)
            step = Step(
                ticket_id=ticket.id,
                idx=step_idx,
                title=tool_input.get("title", f"Step {step_idx}"),
                status=tool_input.get("status", StepStatus.PENDING.value),
                result=json.dumps(tool_input.get("result"))
                if tool_input.get("result")
                else None,
            )
            db.add(step)
            ticket.steps.append(step)
            return f"步骤 {step_idx} 已添加: {step.title}"

        return "Unknown system tool"

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """执行普通工具"""
        executor = get_tool_executor(tool_name)
        if not executor:
            return f"Tool '{tool_name}' not found"

        try:
            result = await executor(tool_input)
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} error: {e}")
            return f"Tool execution error: {str(e)}"

    async def _mark_failed(self, error: str):
        """标记任务失败"""
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
