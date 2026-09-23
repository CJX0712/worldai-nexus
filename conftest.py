"""pytest 根配置: 将仓库根加入 sys.path，确保 `from core import` 可用。"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
