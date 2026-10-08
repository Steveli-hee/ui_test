# -*- coding: utf-8 -*-
"""把 pytest 的 junit.xml 转成一份"能看"的 HTML 测试报告

用法（在项目根 C:\\PyCharmProjects\\ui_test 下）：
    1) python -m pytest --junitxml=报告/junit.xml        # 先让 pytest 产出原始结果
    2) python 报告/生成报告.py                            # 再把结果渲染成 HTML
"""
import html                                    # 用来转义 < > & 等特殊字符，防止页面被内容破坏
import re                                      # 用正则还原 \uXXXX 转义
import xml.etree.ElementTree as ET             # 标准库：解析 XML
from datetime import datetime                  # 记录报告生成时间
from pathlib import Path                       # 用 pathlib 处理路径


def decode_unicode_escapes(text):
    """把 junit 里的 '\u6b63\u786e' 还原成中文
    （pytest 写 junit.xml 时会把非 ASCII 字符转义，直接显示很难看）
    """
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), text)

XML_PATH = Path("报告/junit.xml")               # pytest 产出的原始结果文件
OUT_PATH = Path("报告/测试报告.html")            # 我们要生成的 HTML 报告

# ---------- ① 解析 junit.xml ----------
root = ET.parse(XML_PATH).getroot()             # 得到 <testsuites> 节点
suite = root.find("testsuite") or root          # 找到 <testsuite>（没有就直接用 root）

total = int(suite.get("tests", 0))              # 用例总数
failures = int(suite.get("failures", 0))        # 失败数
errors = int(suite.get("errors", 0))            # 错误数（异常导致，如 fixture 报错）
skipped = int(suite.get("skipped", 0))          # 跳过数
seconds = float(suite.get("time", 0))           # 总耗时（秒）
passed = total - failures - errors - skipped    # 通过数 = 总数 - 其它

rows = []                                        # 收集每条用例的结果，供后面渲染成表格行
for tc in suite.iter("testcase"):                # 遍历每个 <testcase>
    name = decode_unicode_escapes(f"{tc.get('classname', '')}::{tc.get('name', '')}")   # 用例名（还原中文）
    duration = float(tc.get("time", 0))          # 本条耗时
    status, detail = "通过", ""                  # 默认通过、无详情

    failure = tc.find("failure")                 # 断言失败节点
    error = tc.find("error")                     # 异常错误节点
    skip = tc.find("skipped")                    # 跳过节点
    if failure is not None:                      # 有 failure → 断言失败
        status = "失败"
        detail = (failure.get("message") or "") + "\n" + (failure.text or "")
    elif error is not None:                      # 有 error → 抛异常
        status = "错误"
        detail = (error.get("message") or "") + "\n" + (error.text or "")
    elif skip is not None:                       # 有 skipped → 跳过
        status = "跳过"
        detail = skip.get("message", "")

    rows.append((name, status, duration, detail))   # 存起来

# ---------- ② 组装 HTML ----------
tr_list = []                                     # 表格的每一行
for name, status, duration, detail in rows:
    color = {"通过": "#0a7d28", "失败": "#b91c1c", "错误": "#b45309", "跳过": "#666"}[status]  # 状态颜色
    detail_html = ""                             # 失败/错误的详情（默认空）
    if detail.strip():                           # 有详情才生成折叠块
        detail_html = f'<details><summary>查看详情</summary><pre>{html.escape(detail)}</pre></details>'
    tr_list.append(
        f'<tr><td>{html.escape(name)}</td>'
        f'<td style="color:{color};font-weight:bold">{status}</td>'
        f'<td>{duration:.2f}s</td>'
        f'<td>{detail_html}</td></tr>'
    )

summary_cards = (
    f'<div class="card">用例总数<br><b>{total}</b></div>'
    f'<div class="card pass">通过<br><b>{passed}</b></div>'
    f'<div class="card fail">失败<br><b>{failures}</b></div>'
    f'<div class="card warn">错误<br><b>{errors}</b></div>'
    f'<div class="card">跳过<br><b>{skipped}</b></div>'
    f'<div class="card">总耗时<br><b>{seconds:.1f}s</b></div>'
)

HTMl = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>自动化测试报告</title>
<style>
  body {{ font-family: "Microsoft YaHei", sans-serif; max-width: 1100px; margin: 0 auto; padding: 20px; color: #222; }}
  h1 {{ font-size: 22px; }}
  .meta {{ color: #666; font-size: 13px; margin-bottom: 14px; }}
  .cards {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }}
  .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 8px 16px; text-align: center; font-size: 12px; color: #555; }}
  .card b {{ font-size: 20px; display: block; color: #111; }}
  .card.pass b {{ color: #0a7d28; }}
  .card.fail b {{ color: #b91c1c; }}
  .card.warn b {{ color: #b45309; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; vertical-align: top; }}
  th {{ background: #f3f4f6; }}
  pre {{ background: #f8f8f8; padding: 8px; overflow-x: auto; white-space: pre-wrap; }}
  details summary {{ cursor: pointer; color: #1a56db; }}
</style>
</head>
<body>
<h1>迷你商城 · 自动化测试报告</h1>
<div class="meta">生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ｜ 数据来源：junit.xml ｜ 被测系统：迷你商城 (127.0.0.1:5001)</div>
<div class="cards">{summary_cards}</div>
<table>
  <tr><th>用例</th><th>结果</th><th>耗时</th><th>详情</th></tr>
  {''.join(tr_list)}
</table>
</body>
</html>
"""

OUT_PATH.write_text(HTMl, encoding="utf-8")      # 写出 HTML（UTF-8 编码，中文才不乱码）
print(f"报告已生成：{OUT_PATH}（共 {total} 条用例，通过 {passed}，失败 {failures}）")
