"""离线单元测试: Agent 编排 (确定性路由 + RAG)。"""
from agent.react import Agent, build_prompt
from agent.router import is_arithmetic
from embeddings.mock import HashEmbedder
from llm.mock import MockLLM
from retrieval.hybrid import HybridRetriever
from tools.base import ToolRegistry
from tools.calculator import CalculatorTool
from tools.datetime_tool import DateTimeTool
from tools.web_search import WebSearchTool
from vectorstore.memory import InMemoryVectorStore


def _agent():
    retriever = HybridRetriever(HashEmbedder(), InMemoryVectorStore())
    tools = ToolRegistry()
    tools.register(CalculatorTool())
    tools.register(DateTimeTool())
    tools.register(WebSearchTool())
    return Agent(MockLLM(), retriever, tools)


def test_router_arithmetic():
    assert is_arithmetic("12*(3+4)")
    assert not is_arithmetic("hello world")
    assert not is_arithmetic("3 + 4 = ?")  # 含 '=' 不是纯算术，不路由到 calculator


def test_agent_arithmetic_route():
    r = _agent().run("12*(3+4)")
    assert "84" in r.answer
    assert r.tool_calls and r.tool_calls[0].name == "calculator"


def test_agent_rag_route():
    a = _agent()
    a.retriever.add(
        HashEmbedder().embed(["WorldAI Nexus 是晨星打造的世界级模块化 AI 系统。"]),
        ["WorldAI Nexus 是晨星打造的世界级模块化 AI 系统。"],
        [{"chunk_id": "x#0", "doc_id": "x"}],
    )
    r = a.run("WorldAI Nexus 是什么？", k=3)
    assert len(r.sources) >= 1
    assert "晨星" in r.answer or "模块化" in r.answer


def test_build_prompt_format():
    from core.types import SearchHit

    p = build_prompt("Q?", [SearchHit(chunk_id="c1", doc_id="d1", text="KB内容", score=1.0)])
    assert "<kb-context>" in p and "Question: Q?" in p
