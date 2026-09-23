"""WorldAI Nexus - 自包含端到端验证脚本。

替代 docker compose + curl: 拉起真实 HTTP 服务进程，轮询 /health，
再用内置 httpx 跑核心成功流 + 错误流，逐条断言，最后回收子进程。
全部使用 mock 后端，无网络 / 无 Key / 无模型权重即可全绿。

用法: python scripts/verify.py

作者: 晨星
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

import httpx

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.getenv("WORLDAI_VERIFY_PORT", "8123"))
BASE = f"http://127.0.0.1:{PORT}"


def _spawn_server():
    env = dict(os.environ)
    env.update({
        "WORLDAI_LLM": "mock",
        "WORLDAI_EMBEDDER": "mock",
        "WORLDAI_VECTORSTORE": "memory",
        "WORLDAI_PORT": str(PORT),
        "WORLDAI_LOG_LEVEL": "WARNING",
    })
    proc = subprocess.Popen(
        [sys.executable, "-m", "api.main"],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc


def _wait_health(client: httpx.Client, timeout: float = 30.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = client.get("/health")
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("服务未在限定时间内就绪")


def main() -> int:
    proc = _spawn_server()
    passed = 0
    failed = 0
    try:
        with httpx.Client(base_url=BASE, timeout=30.0, trust_env=False) as client:
            h = _wait_health(client)
            print(f"[health] {h}")
            assert h["status"] == "ok"
            passed += 1

            # 入库
            r = client.post("/ingest", json={"text": "WorldAI Nexus 是晨星打造的模块化 AI 系统，支持 RAG 与工具调用。", "doc_id": "verify"})
            assert r.status_code == 200 and r.json()["chunks"] >= 1
            print(f"[ingest] chunks={r.json()['chunks']}")
            passed += 1

            # 算术路由
            r = client.post("/chat", json={"query": "12*(3+4)"})
            assert r.status_code == 200 and "84" in r.json()["answer"]
            print(f"[chat/arith] {r.json()['answer']}")
            passed += 1

            # RAG 问答
            r = client.post("/chat", json={"query": "WorldAI Nexus 是什么？", "k": 3})
            assert r.status_code == 200
            body = r.json()
            assert ("晨星" in body["answer"]) or len(body["sources"]) >= 1
            print(f"[chat/rag] sources={len(body['sources'])}")
            passed += 1

            # 检索
            r = client.post("/search", json={"query": "WorldAI Nexus", "k": 2})
            assert r.status_code == 200 and len(r.json()["hits"]) >= 1
            passed += 1

            # 评估
            r = client.get("/eval")
            assert r.status_code == 200 and r.json()["ok"] is True
            print(f"[eval] {r.json()}")
            passed += 1

            # 错误流: 缺体
            r = client.post("/ingest", json={})
            assert r.status_code == 400
            passed += 1
    except Exception as e:  # noqa
        failed += 1
        print(f"[FAIL] {e}")
        if proc.stdout:
            out = proc.stdout.read().decode("utf-8", "ignore")
            print("--- server log ---\n" + out[-2000:])
    finally:
        if proc.poll() is None:
            try:
                import subprocess as _sp
                _sp.run(["taskkill", "/pid", str(proc.pid), "/t", "/f"], capture_output=True)
            except Exception:
                proc.terminate()

    print(f"\n通过: {passed} / 失败: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
