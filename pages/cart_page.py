# -*- coding: utf-8 -*-
"""购物车/结算页面对象（回归扩展版）
覆盖：首页加购、重复加购、购物车改数量/删除、读总额、读库存、结算
"""


class CartPage:
    """购物车相关页面：首页(加购) → 购物车(改数量/删除) → 结算"""

    CART_PATH = "/cart"                                # 购物车页路径

    def __init__(self, page, base_url="http://127.0.0.1:5001"):
        self.page = page                               # Playwright page 对象
        self.base_url = base_url                       # 站点根地址

    # ==================== 操作区 ====================
    def open_index(self):
        """打开首页（商品列表）"""
        self.page.goto(self.base_url + "/")            # 首页路径
        return self

    def add_to_cart(self, product_name, repeat=1):
        """加购指定商品（可重复加购）
        注意：加购成功后页面会跳到购物车页 → 每次加购前都必须先回到首页，
             否则第二次点击会找不到按钮（这是"用例不健壮"的典型坑）
        """
        for _ in range(repeat):                                    # 需要几件就循环几次
            self.open_index()                                      # 每次加购前先回首页
            card = self.page.locator(".card", has_text=product_name)   # 框定商品卡片
            card.get_by_role("button", name="加入购物车").click()      # 点卡片内按钮
        return self

    def open(self):
        """打开购物车页"""
        self.page.goto(self.base_url + self.CART_PATH)
        return self

    def set_qty(self, product_name, qty):
        """在购物车页把某商品的数量改成 qty，并点该行的『修改』"""
        row = self._row(product_name)                              # 定位到该商品所在行
        row.locator('input[name="qty"]').fill(str(qty))            # 填新数量
        row.get_by_role("button", name="修改").click()              # 点这一行的"修改"
        return self

    def remove(self, product_name):
        """在购物车页删除某商品"""
        row = self._row(product_name)
        row.get_by_role("button", name="删除").click()              # 点这一行的"删除"
        return self

    def checkout(self):
        """点『去结算』"""
        self.page.get_by_role("button", name="去结算").click()
        return self

    # ==================== 读取区 ====================
    def _row(self, product_name):
        """定位购物车表格里某商品所在的行（内部方法，前面加下划线表示不对外用）"""
        return self.page.locator("tr", has_text=product_name)

    def row_text(self, product_name):
        """某商品行的整行文字（含单价/数量/小计）"""
        return self._row(product_name).inner_text()

    @property
    def total_text(self):
        """应付总额那一行的文字"""
        return self.page.locator("tr", has_text="应付总额").inner_text()

    @property
    def page_text(self):
        """整页可见文字"""
        return self.page.locator("body").inner_text()

    @property
    def is_empty(self):
        """购物车是否为空（用于断言空态）"""
        return "购物车是空的" in self.page_text

    def stock_of(self, product_name):
        """首页上某商品的库存数字（从卡片文字里提取，如"（库存 5）"）"""
        self.page.goto(self.base_url + "/")                        # 回首页读库存
        card_text = self.page.locator(".card", has_text=product_name).inner_text()
        # 卡片文字形如："测试专用显示器 ￥899.00 （库存 5） 描述..."，用正则取出库存数字
        import re
        m = re.search(r"库存\s*(\d+)", card_text)
        return int(m.group(1)) if m else -1

    @property
    def url(self):
        return self.page.url

    @property
    def tip(self):
        """顶部提示条文字（没有则空串）"""
        flash = self.page.locator(".flash")
        return flash.inner_text() if flash.count() else ""
