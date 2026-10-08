# -*- coding: utf-8 -*-
"""注册页的页面对象：只负责"这一页怎么操作/怎么读信息"，不含断言"""

class RegisterPage:
    """注册页：一个页面 = 一个类"""

    PATH = "/register"                                  # 类属性：页面路径（固定值）

    def __init__(self, page, base_url="http://127.0.0.1:5001"):
        self.page = page                                # 存下 Playwright 的 page 对象
        self.base_url = base_url                        # 站点根地址

    # ---------------- 操作区 ----------------
    def open(self):
        """打开注册页"""
        self.page.goto(self.base_url + self.PATH)       # 导航到完整地址
        return self                                     # 返回 self → 支持链式调用

    def register(self, phone, password="Abcd1234"):
        """填写并提交注册表单"""
        self.page.locator('input[name="phone"]').fill(phone)          # 手机号框
        self.page.locator('input[name="password"]').fill(password)    # 密码框
        self.page.locator('input[name="password2"]').fill(password)   # 确认密码框
        self.page.get_by_role("button", name="注册").click()           # 点提交
        return self

    # ---------------- 读取区（供断言用） ----------------
    @property
    def url(self):
        """当前页面地址"""
        return self.page.url

    @property
    def tip(self):
        """页面顶部提示条文字（没有提示时返回空串）"""
        flash = self.page.locator(".flash")                   # 定位提示条
        return flash.inner_text() if flash.count() else ""     # 不存在 → 返回 ""