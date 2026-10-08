"""数据驱动（data-driven）示范：用例逻辑不变，数据来自外部 JSON 文件
运行：python -m pytest test_data_driven.py -v
"""
import json
from pathlib import Path          # 用 pathlib 处理文件路径（比字符串拼接可靠）
import pytest
from pages.login_page import LoginPage          # 登录页面对象
from pages.register_page import RegisterPage    # 注册页面对象
from utils import new_phone                     # 唯一手机号工具
# 读取数据文件（encoding 必须写，否则中文在 Windows 上可能乱码）
CASES = json.loads(Path("data/login_cases.json").read_text(encoding="utf-8"))
PHONE = new_phone()          # 本文件共用一个账号（模块级只生成一次）
@pytest.mark.parametrize("case", CASES, ids=[c["场景"] for c in CASES])   # ids → 用例名显示场景名
def test_登录场景_数据驱动(page, case):
    """一条用例逻辑 × 3 组数据 → 3 条用例（数据来自 JSON）"""
    RegisterPage(page).open().register(PHONE)       # 保证账号存在（幂等：已注册也无妨）
    login = LoginPage(page)                         # 造登录页对象
    login.open().login(PHONE, case["password"])     # 用本组数据里的密码登录
    assert login.url.endswith(case["expect_url_end"]), \
        f"【{case['场景']}】落地地址不符：{login.url}"
    if case["expect_tip"]:                          # 需要校验提示文案时才断言
        assert case["expect_tip"] in login.tip, \
            f"【{case['场景']}】提示不符：{login.tip!r}"