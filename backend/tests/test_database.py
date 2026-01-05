"""Database 模块单元测试"""

import pytest


@pytest.mark.unit
class TestDatabase:
    """测试数据库模块"""

    async def test_database_engine_config(self, test_engine):
        """测试数据库引擎配置"""
        assert test_engine is not None
        # 验证是内存数据库
        assert "memory" in str(test_engine.url)

    async def test_database_session(self, db_session):
        """测试数据库会话"""
        assert db_session is not None
        # 测试会话可以执行简单查询
        from sqlalchemy import text

        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    async def test_get_db_generator(self):
        """测试 get_db 生成器"""
        from app.database import get_db

        # get_db 是一个异步生成器
        gen = get_db()
        assert hasattr(gen, "__anext__")
