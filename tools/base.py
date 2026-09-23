"""WorldAI Nexus - Tools 模块: 工具协议与注册表。

Tool 仅依赖 Protocol，运行时注册进 ToolRegistry。Agent 通过名称调用，可插拔、可独立验证。

作者: 晨星
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.types import ToolCall


@runtime_checkable
class Tool(Protocol):
    name: str
    description: str

    def run(self, **kwargs) -> str: ...


class ToolRegistry:
    """工具注册表: 注册 / 按名调用 / 列出元信息。"""
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def run(self, name: str, **kwargs) -> str:
        if name not in self._tools:
            raise KeyError(f"未知工具: {name}")
        return self._tools[name].run(**kwargs)

    def has(self, name: str) -> bool:
        return name in self._tools

    def list(self) -> list[dict]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    def describe(self, call: ToolCall) -> ToolCall:
        return call
