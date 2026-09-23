"""WorldAI Nexus - 共享类型定义 (dataclasses)。

作者: 晨星
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """一份原始文档 (加载后、切分前)。"""
    doc_id: str
    text: str
    source: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    """文档切分后的最小检索单元。"""
    chunk_id: str
    doc_id: str
    text: str
    index: int = 0
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchHit:
    """一次检索命中结果。"""
    chunk_id: str
    doc_id: str
    text: str
    score: float
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatMessage:
    """对话消息。"""
    role: str  # "user" | "assistant" | "system"
    content: str


@dataclass
class ToolCall:
    """一次工具调用记录。"""
    name: str
    args: dict[str, Any]
    result: str | None = None


@dataclass
class AgentResult:
    """Agent 一次推理的完整结果。"""
    answer: str
    sources: list[SearchHit] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""
