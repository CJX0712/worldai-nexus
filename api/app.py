"""WorldAI Nexus - API 层: 应用装配。

作者: 晨星
"""
from __future__ import annotations

from fastapi import FastAPI

from api.routes import make_router
from compose import Container
from core.config import AppConfig


def create_app(config: AppConfig | None = None) -> FastAPI:
    config = config or AppConfig.from_env()
    container = Container(config)
    app = FastAPI(title="WorldAI Nexus", version="1.0.0")
    app.state.container = container
    app.include_router(make_router(container))
    return app
