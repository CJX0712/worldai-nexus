"""WorldAI Nexus - LLM 模块: Mock 离线实现。

启发式确定性回答: 解析 <kb-context> 与 Question: 标记，引用检索到的知识库内容。
无任何外部依赖，保证无网络 / 无 Key 下整链可验证。

作者: 晨星
"""
from __future__ import annotations

import re

from core.types import ChatMessage

_CTX_RE = re.compile(r"<kb-context>\n(.*?)\n</kb-context>", re.S)
_Q_RE = re.compile(r"Question:\s*(.*?)(?:\nAnswer:)?\s*$", re.S)


def _extract(prompt: str) -> tuple[str | None, str]:
    ctx = None
    m = _Q_RE.search(prompt)
    q = m.group(1).strip() if m else ""
    mctx = _CTX_RE.search(prompt)
    if mctx:
        ctx = mctx.group(1).strip()
    return ctx, q


class MockLLM:
    """离线 Mock LLM: 仅做确定性文本拼装，用于链路验证。"""
    name = "mock"

    def __init__(self, model: str = "mock-llm") -> None:
        self.model = model

    def complete(self, prompt: str, **kwargs) -> str:
        ctx, query = _extract(prompt)
        if ctx:
            first = ctx.split("\n", 1)[0]
            first = first[3:].strip() if first.startswith("[1]") else first
            snippet = first[:80]
            return (
                f"根据知识库内容：{snippet}…… "
                f"已基于检索结果为问题「{query}」生成确定性回答。(由晨星AI生成)"
            )
        return f"[MockLLM] 收到问题：{query or prompt[:40]}。这是离线环境下的确定性回答。"

    def chat(self, messages: list[ChatMessage], **kwargs) -> str:
        last = messages[-1].content if messages else ""
        return self.complete(last)
