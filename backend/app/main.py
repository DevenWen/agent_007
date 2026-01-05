"""Agent Platform Backend - FastAPI Application"""

# 初始化日志配置（必须在其他模块导入前完成）
from app.logging_config import setup_logging

setup_logging()

# 加载 .env 文件（必须在 config 导入前完成）
# override=True 确保 .env 中的值覆盖系统环境变量
from dotenv import load_dotenv

load_dotenv(override=True)

from contextlib import asynccontextmanager  # noqa: E402
import logging

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.config import CORS_ORIGINS, API_PREFIX  # noqa: E402
from app.database import init_db  # noqa: E402
from app.routers import agents, tools, tickets, sessions  # noqa: E402

# 导入所有 tools 模块以触发注册
# 注意：这很重要，否则 registry 中为空
import app.tools.file_tools  # noqa: F401
import app.tools.command_tools  # noqa: F401
import app.tools.search_tools  # noqa: F401
import app.tools.http_tools  # noqa: F401
import app.tools.calculator  # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()

    from app.database import async_session_maker
    from app.tools.sync import sync_tools_to_database

    # 自动同步 Tools 到数据库
    async with async_session_maker() as db:
        logger.info("Syncing tools to database...")
        await sync_tools_to_database(db)

    # 启动调度器
    from app.scheduler import Dispatcher

    dispatcher = Dispatcher()
    await dispatcher.start()

    yield

    # 关闭时清理
    dispatcher.stop()


app = FastAPI(
    title="Agent Platform API",
    version="0.0.1",
    description="Agent Platform MVP Backend",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(agents.router, prefix=API_PREFIX)
app.include_router(tools.router, prefix=API_PREFIX)
app.include_router(tickets.router, prefix=API_PREFIX)
app.include_router(sessions.router, prefix=API_PREFIX)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}
