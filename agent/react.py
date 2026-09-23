"""WorldAI Nexus - Agent 模块: 编排中枢 (ReAct 风格)。

单一职责: 接收查询 -> 确定性路由 -> (工具 或 RAG检索+LLM) -> 返回带引用来源的结果。
依赖 LLMProvider / Retriever / ToolRegistry 三个 Protocol，运行时注入，可独立验证。

作者: 晨星
"""
from __future__ import annotations

from core.types import AgentResult, SearchHit, ToolCall


def build_prompt(query: str, sources: list[SearchHit]) -> str:
    """构造带 <kb-context> 与 Question: 标记的提示词 (分隔符全局唯一，避免与指令文本撞名)。"""
    ctx = ""
    if sources:
        lines = [f"[{i}] {h.text}" for i, h in enumerate(sources, 1)]
        ctx = "<kb-context>\n" + "\n".join(lines) + "\n</kb-context>\n"
    return f"{ctx}Question: {query}\nAnswer:"


class Agent:
    def __init__(self, llm, retriever, tools, use_rag: bool = True) -> None:
        self.llm = llm
        self.retriever = retriever
        self.tools = tools
        self.use_rag = use_rag

    def run(self, query: str, k: int = 5) -> AgentResult:
        tool_calls: list[ToolCall] = []

        # 1) 确定性路由: 算术 -> calculator
        from agent.router import is_arithmetic

        if is_arithmetic(query):
            res = self.tools.run("calculator", expression=query)
            tool_calls.append(ToolCall(name="calculator", args={"expression": query}, result=res))
            return AgentResult(
                answer=f"计算结果：{res}",
                sources=[],
                tool_calls=tool_calls,
                model=self.llm.name,
            )

        # 2) RAG 检索
        sources = self.retriever.search(query, k=k) if self.use_rag else []

        # 3) 组装提示词并调用 LLM
        prompt = build_prompt(query, sources)
        answer = self.llm.complete(prompt)

        return AgentResult(
            answer=answer,
            sources=sources,
            tool_calls=tool_calls,
            model=self.llm.name,
        )
