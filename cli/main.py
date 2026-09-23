"""WorldAI Nexus - CLI 入口。

子命令:
  ingest  从文件 / 标准输入 / --text 入库
  ask     向 Agent 提问 (自动路由工具 / RAG)
  eval    运行内置评估套件
  serve   启动 HTTP 服务 (同 api.main)

作者: 晨星
"""
from __future__ import annotations

import argparse
import sys

from compose import Container
from core.config import AppConfig
from core.logging import setup_logging


def _build() -> Container:
    config = AppConfig.from_env()
    setup_logging(config.log_level)
    return Container(config)


def cmd_ingest(args, c: Container) -> int:
    if args.file:
        chunks = c.ingest_file(args.file)
    else:
        text = sys.stdin.read() if args.text is None else args.text
        if not text.strip():
            print("错误: 未提供文本 (用 --text 或管道输入)", file=sys.stderr)
            return 2
        chunks = c.ingest_text(text, args.doc_id)
    print(f"已入库分块数: {len(chunks)}")
    return 0


def cmd_ask(args, c: Container) -> int:
    result = c.agent.run(args.query, k=args.k)
    print("回答:", result.answer)
    if result.sources:
        print("\n来源:")
        for s in result.sources:
            snippet = s.text[:80].replace("\n", " ")
            print(f"  - [{s.doc_id}] {snippet} (score={s.score:.3f})")
    return 0


def cmd_eval(args, c: Container) -> int:
    from eval import run_eval

    passed, total = run_eval(c)
    print(f"评估通过: {passed}/{total}")
    return 0 if passed == total else 1


def cmd_serve(args, c: Container) -> int:
    import uvicorn

    config = AppConfig.from_env()
    from api.app import create_app

    app = create_app(config)
    uvicorn.run(app, host=config.host, port=config.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="worldai", description="WorldAI Nexus 命令行")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("ingest", help="入库文档")
    pi.add_argument("--file", help="文件路径 (.txt/.md/.pdf)")
    pi.add_argument("--text", help="直接文本")
    pi.add_argument("--doc-id", default="mem")
    pi.set_defaults(func=cmd_ingest)

    pa = sub.add_parser("ask", help="向 Agent 提问")
    pa.add_argument("query", help="问题")
    pa.add_argument("--k", type=int, default=5)
    pa.set_defaults(func=cmd_ask)

    pe = sub.add_parser("eval", help="运行评估")
    pe.set_defaults(func=cmd_eval)

    ps = sub.add_parser("serve", help="启动 HTTP 服务")
    ps.set_defaults(func=cmd_serve)
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    c = _build()
    return args.func(args, c)


if __name__ == "__main__":
    raise SystemExit(main())
