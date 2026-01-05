"""Agent Platform Backend - Configuration"""

import os
from pathlib import Path


# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/data/agent_platform.db"
)

# API 配置
API_PREFIX = os.getenv("API_PREFIX", "/api")

# 调度器配置
SCHEDULER_INTERVAL = float(os.getenv("SCHEDULER_INTERVAL", "2.0"))

# CORS 配置
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
).split(",")
