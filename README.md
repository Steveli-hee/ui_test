# 迷你商城 · 自动化测试项目
## 项目简介
对自研「迷你商城」（Flask + SQLite）进行 UI 与接口自动化测试， 覆盖注册登录、购物车、结算、库存边界等核心链路。

## 技术栈
Python 3.11 ｜ pytest 9.1.1 ｜ Playwright（UI）｜ requests（接口）｜ Page Object 模式

## 目录结构
pages/ 页面对象（register / login / cart） data/ 数据驱动用的 JSON 数据 报告/ 测试报告生成脚本与产物 test_smoke.py / test_regression_cart.py / test_login_po.py / test_data_driven.py

## 如何运行
启动被测系统：cd 被测系统\mini_mall && python app.py（或双击 启动商城.bat）
冒烟测试（约 3.5 秒）：python -m pytest -m smoke -v
回归测试：python -m pytest -m regression -v
生成报告：python -m pytest --junitxml=报告/junit.xml → python 报告/生成报告.py
## 测试成果
| 项目   | 数据                                   |
|------|--------------------------------------|
| 用例总数 | 21 条（冒烟 4 / 回归 9 / 其他 8）             |
| 冒烟套件 | 4 条全部通过，耗时 3.8 秒                     |
| 回归套件 | 9 条（5 通过 / 4 条为待修复缺陷的预期失败 XFAIL）     |
| 全量执行 | 21 条：16 通过 / 1 失败 / 4 预期失败，耗时 22.8 秒 |
| 发现缺陷 | 8 个（BUG1~BUG8）+ 1 项可测性改进建议           |
| 测试报告 | 报告/测试报告.html（全量）、报告/冒烟报告.html（冒烟）    |