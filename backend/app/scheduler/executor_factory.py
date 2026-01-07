import os
from app.scheduler.base_executor import IExecutor
from app.scheduler.executor import AnthropicExecutor
from app.scheduler.executor2 import SDKExecutor


class ExecutorFactory:
    """Executor 工厂"""

    @staticmethod
    def create_executor(ticket_id: str, session_id: str) -> IExecutor:
        """创建 Executor 实例"""
        # 可以通过环境变量或配置切换 Executor 实现
        executor_type = os.getenv(
            "EXECUTOR_TYPE", "anthropic_api"
        )  # default to anthropic

        if executor_type == "claude_agent_sdk":
            return SDKExecutor(ticket_id, session_id)
        else:
            return AnthropicExecutor(ticket_id, session_id)
