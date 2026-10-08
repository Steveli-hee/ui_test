"""登录页的页面对象：只负责"登录页怎么操作"，不含断言"""
class LoginPage:
    """登录页：一个页面 = 一个类"""
    PATH = "/login"                            # 类属性：页面路径（固定不变的东西放类属性）
    def __init__(self, page, base_url="http://127.0.0.1:5001"):
        self.page = page                       # 存下 Playwright 的 pages，后面操作都靠它
        self.base_url = base_url               # 站点根地址
    # ---------------- 操作区 ----------------
    def open(self):
        """打开登录页"""
        self.page.goto(self.base_url + self.PATH)   # 拼出完整地址并导航
        return self                                 # 返回 self → 支持链式调用 open().login()
    def login(self, phone, password):
        """填手机号 + 密码，点登录按钮"""
        self.page.locator('input[name="phone"]').fill(phone)        # 手机号框（属性定位）
        self.page.locator('input[name="password"]').fill(password)  # 密码框
        self.page.get_by_role("button", name="登录").click()         # 按"角色+名称"点提交
        return self
    # ---------------- 读取区（供断言用） ----------------
    @property
    def url(self):
        """当前页面地址（@property → 用 login.url 而不是 login.url()）"""
        return self.page.url
    @property
    def tip(self):
        """页面顶部黄色提示条文字；没有提示时返回空字符串"""
        flash = self.page.locator(".flash")             # 定位提示条
        return flash.inner_text() if flash.count() else ""   # 不存在就返回 ""（避免报错）