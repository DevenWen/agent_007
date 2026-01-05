"""日志配置模块 - 统一配置日志输出到文件和控制台"""

import logging
from datetime import datetime
from pathlib import Path

# 日志目录
LOG_DIR = Path(__file__).parent.parent / ".log"


def setup_logging():
    """配置日志系统"""
    # 确保日志目录存在
    LOG_DIR.mkdir(exist_ok=True)

    # 日志文件名（按日期）
    log_file = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

    # 日志格式
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 清除已有的 handler（避免重复添加）
    root_logger.handlers.clear()

    # 控制台 Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # 临时改为 DEBUG 级别用于调试
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console_handler)

    # 文件 Handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # 文件记录更详细的日志
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(file_handler)

    # 降低第三方库的日志级别
    # logging.getLogger("httpx").setLevel(logging.WARNING)
    # logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    logging.info(f"Logging initialized, log file: {log_file}")
