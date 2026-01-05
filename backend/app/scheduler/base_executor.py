from abc import ABC, abstractmethod


class IExecutor(ABC):
    """Executor Interface"""

    @abstractmethod
    def __init__(self, ticket_id: str, session_id: str):
        pass

    @abstractmethod
    async def run(self):
        """运行任务"""
        pass

    @abstractmethod
    def stop(self):
        """停止任务"""
        pass
