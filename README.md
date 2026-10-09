# 迷你商城 · 自动化测试项目
## 项目简介
对自研「迷你商城」（Flask + SQLite）进行 UI 与接口自动化测试， 覆盖注册登录、购物车、结算、库存边界等核心链路。

## 技术栈
Python 3.11 ｜ pytest 9.1.1 ｜ Playwright（UI）｜ requests（接口）｜ Page Object 模式

## 目录结构
tests/ 用例（ 冒烟/回归/PageObject/数据驱动） 
pages/ 页面对象（register / login / cart） 
data/ 数据驱动用的测试数据 报告/ 报告生成脚本与报告产物 
system_under_test/mini_mall/ 被测系统（Flask + SQLite，含 8 个已埋缺陷） 
conftest.py 
utils.py 
pytest.ini


## 如何运行
启动被测系统（新开一个终端）：
cd system_under_test/mini_mall
pip install flask
python app.py            # 看到"迷你商城已启动"即成功
冒烟测试（约 4~6 秒）：python -m pytest -m smoke -v
回归测试（17 条）：python -m pytest -m regression -v
生成报告：python -m pytest --junitxml=报告/junit.xml → python 报告/生成报告.py

## 测试成果
| 项目   | 数据                                        |
|------|-------------------------------------------|
| 用例总数 | 21 条（冒烟 4 / 回归 17）                        |
| 冒烟套件 | 4 条全部通过，耗时约 4~6 秒                         |
| 回归套件 | 17 条（13 通过 / 4 条为待修复缺陷的预期失败 XFAIL）        |
| 全量执行 | 21 条：16 通过 / 1 失败（BUG3待修复）/ 4 预期失败，约 23 秒 |
| 发现缺陷 | 8 个（BUG1~BUG8）+ 1 项可测性改进建议                |
| 测试报告 | 报告/测试报告.html（全量）、报告/冒烟报告.html（冒烟）         |
| CI   | 	GitHub Actions：每次 push 自动启动被测系统并跑冒烟测试    |