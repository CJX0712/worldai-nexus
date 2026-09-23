"""WorldAI Nexus - Tools 模块: 联网搜索 (占位实现)。

真实检索后端可在此处注入 (如 SerpAPI / Bing / 自建爬虫)，接口保持不变。
默认返回占位说明，避免无网络时链路中断。

作者: 晨星
"""
from __future__ import annotations


class WebSearchTool:
    name = "web_search"
    description = "联网搜索。当前为占位实现，可注入真实检索后端。"

    def run(self, query: str = "", **kwargs) -> str:
        q = query or kwargs.get("query", "")
        return f"[web_search 占位] 未配置搜索引擎，查询: {q}"
