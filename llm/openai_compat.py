"""WorldAI Nexus - LLM 模块: OpenAI 兼容后端。

兼容任意 OpenAI 兼容服务: 本地 Ollama、vLLM、LM Studio、OpenAI 官方等。
指向 localhost 时强制 trust_env=False，避免被系统 SOCKS/HTTP 代理劫持 (已知 WinError 10054 坑)。

作者: 晨星
"""
from __future__ import annotations

import httpx

from core.types import ChatMessage


class OpenAICompatLLM:
    """OpenAI 兼容 Chat Completions 后端。"""
    name = "openai-compat"

    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def complete(self, prompt: str, **kwargs) -> str:
        return self.chat([ChatMessage(role="user", content=prompt)], **kwargs)

    def chat(self, messages: list[ChatMessage], **kwargs) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": kwargs.get("temperature", 0.2),
        }
        # trust_env=False: 防止本机流量被代理拦截
        with httpx.Client(base_url=self.base_url, timeout=self.timeout, trust_env=False) as client:
            resp = client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]
