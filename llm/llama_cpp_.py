"""WorldAI Nexus - LLM 模块: 本地 GGUF 模型 (llama.cpp)。

使用 llama-cpp-python 在 CPU/GPU 本地推理，零外网依赖。仅在使用 llamacpp 提供方时加载。

作者: 晨星
"""
from __future__ import annotations

from core.errors import ProviderError
from core.types import ChatMessage


class LlamaCppLLM:
    """本地 GGUF 大模型推理。"""
    name = "llamacpp"

    def __init__(self, model_path: str, n_ctx: int = 4096, n_threads: int = 4) -> None:
        if not model_path:
            raise ProviderError("llamacpp 提供方需要设置 WORLDAI_LLAMA_MODEL 模型路径")
        try:
            from llama_cpp import Llama
        except ImportError as exc:  # pragma: no cover
            raise ProviderError("未安装 llama-cpp-python，请执行 pip install llama-cpp-python") from exc
        self._llm = Llama(model_path=model_path, n_ctx=n_ctx, n_threads=n_threads)
        self.model = model_path

    def complete(self, prompt: str, **kwargs) -> str:
        out = self._llm(prompt, max_tokens=kwargs.get("max_tokens", 512))
        return out["choices"][0]["text"]

    def chat(self, messages: list[ChatMessage], **kwargs) -> str:
        prompt = "\n".join(f"{m.role}: {m.content}" for m in messages)
        return self.complete(prompt, **kwargs)
