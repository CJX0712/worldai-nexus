"""离线单元测试: 工具 (calculator / datetime)。"""
import re
from tools.calculator import CalculatorTool, _safe_eval
from tools.datetime_tool import DateTimeTool


def test_calculator_basic():
    c = CalculatorTool()
    assert c.run(expression="12*(3+4)") == "84"
    assert c.run(expression="2**10") == "1024"
    assert c.run(expression="100/4") == "25"


def test_calculator_rejects_injection():
    c = CalculatorTool()
    # 名称/调用/属性访问应被拒绝
    assert "失败" in c.run(expression="__import__('os').system('echo hi')")
    assert "失败" in c.run(expression="open('x')")


def test_safe_eval_whitelist():
    assert _safe_eval("3 + 4 * 2") == 11.0
    try:
        _safe_eval("x.y")
        assert False, "应拒绝属性访问"
    except ValueError:
        pass


def test_datetime_format():
    out = DateTimeTool().run()
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", out)
