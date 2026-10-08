import pytest
import requests                                        # 用来探活被测服务
from playwright.sync_api import sync_playwright

from pages.cart_page import CartPage                   # 购物车页面对象
from pages.login_page import LoginPage                 # 登录页面对象
from pages.register_page import RegisterPage           # 注册页面对象
from utils import new_phone                            # 唯一手机号工具

HOST = "127.0.0.1:5001"                                # 不写 http:// 防复制污染
BASE = "http://" + HOST


@pytest.fixture(scope="session", autouse=True)
def 服务可用():
    """会话级前置条件：商城必须在跑，否则整批 skip（而不是伪装成失败）"""
    try:
        requests.get(BASE + "/", timeout=3)
    except requests.ConnectionError:
        pytest.skip("迷你商城未启动：cd 被测系统/mini_mall && python app.py")


@pytest.fixture
def page():
    """提供 Playwright 页面：用例结束自动关浏览器"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)     # headless=False 可看操作过程
        pg = browser.new_page()
        yield pg                                       # 把 page 借给用例
        browser.close()


@pytest.fixture
def 已登录购物车(page):
    """前置：注册一个全新用户并登录，返回购物车页面对象
    用例拿到的就是"已登录且购物车为空"的状态 —— 前置统一放 fixture 里，用例只写业务
    """
    phone = new_phone()                                # 唯一手机号（数据三原则：唯一）
    RegisterPage(page).open().register(phone)          # 注册
    LoginPage(page).open().login(phone, "Abcd1234")    # 登录
    return CartPage(page)                              # 把购物车对象交给用例
