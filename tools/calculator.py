"""WorldAI Nexus - Tools 模块: 安全计算器。

使用 AST 白名单解析算术表达式，仅允许数字与 + - * / % ** 以及括号与一元负号，
拒绝任何名称/属性/调用，杜绝代码注入。确定性前置路由会优先把算术交给它，避免小模型重算出错。

作者: 晨星
"""
from __future__ import annotations

import ast
import operator

_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_eval(expr: str) -> float:
    try:
        node = ast.parse(expr, mode="eval").body
    except SyntaxError as exc:
        raise ValueError(f"表达式语法错误: {expr}") from exc
    return _eval_node(node)


def _eval_node(node: ast.AST):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("仅支持数值常量")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _ALLOWED_BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_eval_node(node.operand))
    raise ValueError("表达式含不允许的操作")


class CalculatorTool:
    name = "calculator"
    description = "计算算术表达式，例如 12*(3+4)。仅支持 + - * / % ** 与括号。"

    def run(self, expression: str = "", **kwargs) -> str:
        expr = expression or kwargs.get("expression", "")
        if not expr:
            return "未提供表达式"
        try:
            result = _safe_eval(expr)
        except (ValueError, ZeroDivisionError) as exc:
            return f"计算失败: {exc}"
        if result == int(result):
            return str(int(result))
        return repr(result)
