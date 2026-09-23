"""WorldAI Nexus - API 层: 启动入口。

作者: 晨星
"""
from __future__ import annotations

import uvicorn

from api.app import create_app
from core.config import AppConfig
from core.logging import setup_logging


def main() -> None:
    config = AppConfig.from_env()
    setup_logging(config.log_level)
    app = create_app(config)
    uvicorn.run(app, host=config.host, port=config.port)


if __name__ == "__main__":
    main()
