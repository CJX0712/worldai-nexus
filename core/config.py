"""WorldAI Nexus - 配置层。

通过环境变量选择各模块的"实现"，实现 Protocol 与运行时注入解耦。
默认全部走零依赖 Mock 实现，保证无网络 / 无 Key / 无模型权重下整链可跑。

作者: 晨星
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    # ---- 模块实现选择 ----
    llm_provider: str = "mock"          # mock | openai | llamacpp
    embedder: str = "mock"              # mock | fastembed
    vectorstore: str = "memory"         # memory | faiss

    # ---- 路径 ----
    data_dir: Path = Path("./data")

    # ---- LLM (OpenAI 兼容 / llama.cpp) ----
    openai_base_url: str = "http://localhost:11434/v1"
    openai_api_key: str = "sk-no-key"
    openai_model: str = "local-model"
    llama_model_path: str = ""

    # ---- 嵌入 ----
    embed_model: str = "BAAI/bge-small-en-v1.5"

    # ---- 服务 ----
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            llm_provider=os.getenv("WORLDAI_LLM", "mock"),
            embedder=os.getenv("WORLDAI_EMBEDDER", "mock"),
            vectorstore=os.getenv("WORLDAI_VECTORSTORE", "memory"),
            data_dir=Path(os.getenv("WORLDAI_DATA_DIR", "./data")),
            openai_base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
            openai_api_key=os.getenv("OPENAI_API_KEY", "sk-no-key"),
            openai_model=os.getenv("OPENAI_MODEL", "local-model"),
            llama_model_path=os.getenv("WORLDAI_LLAMA_MODEL", ""),
            embed_model=os.getenv("WORLDAI_EMBED_MODEL", "BAAI/bge-small-en-v1.5"),
            host=os.getenv("WORLDAI_HOST", "0.0.0.0"),
            port=int(os.getenv("WORLDAI_PORT", "8000")),
            log_level=os.getenv("WORLDAI_LOG_LEVEL", "INFO"),
        )
