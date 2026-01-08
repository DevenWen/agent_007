import json
import logging
from app.tools.registry import register_tool
from app.scheduler.context import execution_context
from app.models.step import Step

# Status enums are strings in models, but nice to have constants if available.
# We will use string literals or import if needed.
from app.models.ticket import TicketStatus
from app.models.session import SessionStatus

logger = logging.getLogger(__name__)


@register_tool(
    name="request_human_input",
    description="请求人工介入，暂停任务等待用户输入。当你需要用户提供额外信息、确认操作或做出决策时使用此工具。",
    input_schema={"prompt": str},
)
async def request_human_input(args: dict) -> dict:
    """请求人工介入 - 符合 SDK 工具格式"""
    prompt = args.get("prompt", "")

    ctx = execution_context.get()
    db = ctx.db
    ticket = ctx.ticket
    session = ctx.session
    executor = ctx.executor

    ticket.status = TicketStatus.SUSPENDED.value
    session.status = SessionStatus.SUSPENDED.value
    await db.commit()
    executor.stop()

    logger.info(f"Ticket {ticket.id[:8]} suspended for human input")
    return {
        "content": [
            {"type": "text", "text": f"任务已挂起，等待用户输入。提示: {prompt}"}
        ]
    }


@register_tool(
    name="complete_task",
    description="标记任务完成。当任务目标已达成时调用此工具。",
    input_schema={"summary": str},
)
async def complete_task(args: dict) -> dict:
    """标记任务完成 - 符合 SDK 工具格式"""
    logger.info(f"complete_task CALLED with args: {args}")
    summary = args.get("summary", "")

    ctx = execution_context.get()
    db = ctx.db
    ticket = ctx.ticket
    session = ctx.session
    executor = ctx.executor

    ticket.status = TicketStatus.COMPLETED.value
    session.status = SessionStatus.COMPLETED.value

    # Commit status changes immediately
    await db.commit()

    executor.stop()

    logger.info(f"Ticket {ticket.id[:8]} completed")
    return {"content": [{"type": "text", "text": f"任务已完成。摘要: {summary}"}]}


@register_tool(
    name="fail_task",
    description="标记任务失败。当遇到无法恢复的错误时调用此工具。",
    input_schema={"error": str},
)
async def fail_task(args: dict) -> dict:
    """标记任务失败 - 符合 SDK 工具格式"""
    error = args.get("error", "")

    ctx = execution_context.get()
    db = ctx.db
    ticket = ctx.ticket
    session = ctx.session
    executor = ctx.executor

    ticket.status = TicketStatus.FAILED.value
    ticket.error_message = error
    session.status = SessionStatus.FAILED.value
    await db.commit()
    executor.stop()

    logger.info(f"Ticket {ticket.id[:8]} failed: {error}")
    return {"content": [{"type": "text", "text": f"任务已标记为失败。错误: {error}"}]}


# TODO 增加要给完成 step 的 tools


@register_tool(
    name="add_step",
    description="添加一个任务步骤。用于记录任务的子步骤进度。",
    input_schema={"title": str, "status": str},
)
async def add_step(args: dict) -> dict:
    """添加任务步骤 - 符合 SDK 工具格式"""
    title = args.get("title", "")
    status = args.get("status", "pending")

    ctx = execution_context.get()
    ticket = ctx.ticket
    db = ctx.db

    step_idx = len(ticket.steps)
    step = Step(
        ticket_id=ticket.id, idx=step_idx, title=title, status=status, result=None
    )
    db.add(step)
    ticket.steps.append(step)
    await db.commit()

    return {"content": [{"type": "text", "text": f"步骤 {step_idx} 已添加: {title}"}]}
