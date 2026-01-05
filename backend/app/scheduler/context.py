from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any


@dataclass
class ExecutionContext:
    db: Any
    ticket: Any
    session: Any
    executor: Any


# Context variable to hold the current execution context
execution_context: ContextVar[ExecutionContext] = ContextVar("execution_context")
