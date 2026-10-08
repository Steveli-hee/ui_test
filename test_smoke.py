# -*- coding: utf-8 -*-
"""冒烟套件：只跑主链路。运行：python -m pytest -m smoke -v"""
import pytest

from pages.cart_page import CartPage           # 购物车/结算页面对象
from pages.login_page import LoginPage         # 登录页面对象
from pages.register_page import RegisterPage   # 注册页面对象
from utils import new_phone                    # 唯一手机号工具

@pytest.mark.smoke                             # 打上冒烟标记 → -m smoke 能筛到
def test_冒烟_主链路_注册登录加购下单(page):
    """主链路：注册 → 登录 → 加购 → 结算 → 下单成功"""
    phone = new_phone()                                     # ① 造唯一数据（用例自包含）
    RegisterPage(page).open().register(phone)               # ② 注册

    login = LoginPage(page)                                 # ③ 登录（商城注册后不自动登录，故显式登录）
    login.open().login(phone, "Abcd1234")
    assert login.url.endswith("/"), f"登录失败，当前地址：{login.url}"

    cart = CartPage(page)                                   # ④ 加购
    cart.open_index().add_to_cart("保温杯")                   # 在首页点该商品的加入购物车
    cart.open()                                             # ⑤ 进购物车
    assert "保温杯" in cart.page_text, "购物车里没看到刚加的商品"
    cart.checkout()                                         # ⑥ 去结算

    assert "下单成功" in cart.page_text, f"下单失败：{cart.page_text[:80]}"

@pytest.mark.smoke
def test_冒烟_未登录加购应被拦截(page):
    """未登录点『加入购物车』→ 应被踢到登录页并提示"请先登录"""
    cart = CartPage(page)
    cart.open_index().add_to_cart("保温杯")                   # 未登录直接加购
    assert "/login" in cart.url, f"没被拦截，地址：{cart.url}"
    assert "请先登录" in cart.tip, f"提示不对：{cart.tip!r}"

@pytest.mark.smoke
def test_冒烟_首页可访问(page):
    """最基础：首页能打开、标题正确"""
    CartPage(page).open_index()
    assert "迷你商城" in page.title(), f"标题异常：{page.title()}"

@pytest.mark.smoke
def test_冒烟_首页至少有3个商品(page):
    """首页商品列表至少展示 3 个商品（商品列表功能没被改坏）"""
    CartPage(page).open_index() # 动作：打开首页
    count = page.locator(".card").count()# 读取：数商品卡片数量（count 不收参数！）
    assert count >= 3 # 断言：顺带把实际数量报出来

