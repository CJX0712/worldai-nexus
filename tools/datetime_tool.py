"""WorldAI Nexus - Tools 模块: 当前时间工具。

作者: 晨星
"""
from __future__ import annotations

from datetime import datetime


class DateTimeTool:
    name = "datetime"
    description = "返回当前系统日期时间 (YYYY-MM-DD HH:MM:SS)。"

    def run(self, **kwargs) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
