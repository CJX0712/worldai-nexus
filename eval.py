"""WorldAI Nexus - 内置评估套件。

供 CLI `eval` 与 API `/eval` 复用: 在干净容器上跑确定性断言，返回 (通过数, 总数)。
覆盖: 算术路由 / 入库后 RAG 回答 / 检索召回。

作者: 晨星
"""
from __future__ import annotations


def run_eval(container) -> tuple[int, int]:
    total = 0
    passed = 0

    # 1) 算术路由 -> calculator
    total += 1
    r1 = container.agent.run("12*(3+4)")
    if "84" in r1.answer:
        passed += 1

    # 2) 入库后 RAG 回答引用知识库
    container.ingest_text(
        "WorldAI Nexus 是晨星打造的世界级模块化 AI 系统，支持 RAG 与工具调用。",
        doc_id="eval-doc",
    )
    total += 1
    r2 = container.agent.run("WorldAI Nexus 是什么？", k=3)
    if r2.sources or ("晨星" in r2.answer) or ("模块化" in r2.answer):
        passed += 1

    # 3) 检索召回
    total += 1
    hits = container.retriever.search("WorldAI Nexus", k=1)
    if hits:
        passed += 1

    return passed, total
