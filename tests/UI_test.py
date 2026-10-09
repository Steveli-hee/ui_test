import pytest
import time
HOST = "127.0.0.1:5001"
BASE = "http://" + HOST

@pytest.mark.regression
def test_首页标题正确(page):
    page.goto(BASE + "/")
    assert "迷你商城" in page.title()

@pytest.mark.regression
def test_未登录点击购物车应跳转登录页(page):
    page.goto(BASE + "/")  # 动作
    page.get_by_role("link", name="购物车").click()
    assert "/login" in page.url

@pytest.mark.regression
def test_注册成功后应自动登录进首页(page):
    phone = f"137{int(time.time()) % 100000000:08d}"
    page.goto(BASE + "/")
    page.get_by_role("link", name="注册").click()  # ① 点注册
    page.locator('input[name="phone"]').fill(phone)  # ② 填手机号
    page.locator('input[name="password"]').fill("Abcd1234")  # ③ 两次密码
    page.locator('input[name="password2"]').fill("Abcd1234")
    page.get_by_role("button", name="注册").click()  # ④ 提交
    assert page.url == BASE + "/"  # 现在这条会 FAILED = BUG3 铁证
