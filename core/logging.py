"""WorldAI Nexus - 日志初始化 (loguru)。

作者: 晨星
"""
from __future__ import annotations

import sys

from loguru import logger


def setup_logging(level: str = "INFO") -> None:
    """配置全局日志格式与级别。"""
    logger.remove()
    logger.add(
        sys.stderr,
        level=level.upper(),
        format=(
            "<green>{time:HH:mm:ss}</green> "
            "<level>{level: <8}</level> "
            "<cyan>{name}</cyan> {message}"
        ),
    )
