"""WorldAI Nexus - P0 门禁: 全仓 emoji 扫描。

禁止将 emoji 用作功能图标 / 装饰。源码与文档中不得出现 emoji 码点。
发现即退出码 1，阻断交付。

作者: 晨星
"""
from __future__ import annotations

import os
import re
import sys

# 目标文件类型
SCAN_EXT = {".py", ".html", ".htm", ".md", ".txt", ".yaml", ".yml", ".toml", ".json", ".css", ".js"}
SKIP_DIRS = {".git", "node_modules", "data", "dist", "build", "__pycache__", ".venv", "venv"}

# emoji 码点区间 (整数)，用 chr() 显式构建，避免 \U 转义歧义
_EMOJI_RANGES = [
    (0x1F300, 0x1FAFF),
    (0x1F900, 0x1F9FF),
    (0x2600, 0x27BF),
    (0x1F000, 0x1F02F),
    (0x1F1E6, 0x1F1FF),
    (0x2B00, 0x2BFF),
    (0xFE00, 0xFE0F),
    (0x200D, 0x200D),
    (0xE0020, 0xE007F),
]
_PATTERN = "[" + "".join(f"{chr(s)}-{chr(e)}" for s, e in _EMOJI_RANGES) + "]"
_EMOJI_RE = re.compile(_PATTERN)


def scan(root: str) -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in SCAN_EXT:
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    for ln, line in enumerate(fh, 1):
                        for m in _EMOJI_RE.finditer(line):
                            hits.append((os.path.relpath(path, root), ln, m.group(0)))
            except (UnicodeDecodeError, OSError):
                continue
    return hits


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hits = scan(root)
    if not hits:
        print("[scan_emoji] OK - 未发现 emoji")
        return 0
    print(f"[scan_emoji] 发现 {len(hits)} 处 emoji 违规:")
    for path, ln, ch in hits:
        print(f"  {path}:{ln}  {ch!r}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
