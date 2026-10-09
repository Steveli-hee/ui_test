# -*- coding: utf-8 -*-
"""登录用例：只写业务步骤 + 断言，定位细节都在 pages 里"""
import pytest
from pages.login_page import LoginPage                  # 导入登录页对象
from pages.register_page import RegisterPage
from utils import new_phone  # 导入注册页对象和唯一手机号工具

@pytest.mark.regression
def test_登录成功后应进入首页(page):
    phone = new_phone()                                 # ① 准备数据：唯一手机号
    RegisterPage(page).open().register(phone)           # ② 先注册（用例自包含，不依赖历史数据）
    login = LoginPage(page)                             # ③ 造登录页对象
    login.open().login(phone, "Abcd1234")               # ④ 打开登录页并登录
    assert login.url.endswith("/"), f"登录后地址异常：{login.url}"   # ⑤ 断言落在首页

@pytest.mark.regression
def test_密码错误应有提示(page):
    phone = new_phone()
    RegisterPage(page).open().register(phone)           # 先保证账号存在（否则测的是"账号不存在"）
    login = LoginPage(page)
    login.open().login(phone, "WrongPass1")             # 用错误密码登录
    assert "密码错误" in login.tip, f"实际提示：{login.tip!r}"       # 断言提示文案