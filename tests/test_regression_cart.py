# -*- coding: utf-8 -*-
"""回归套件：购物车 / 结算 / 库存边界
运行：python -m pytest -m regression -v
前置：已登录购物车 fixture（注册新用户 + 登录）
"""
import pytest

# ---------- 购物车明细 ----------

@pytest.mark.regression
@pytest.mark.xfail(reason="BUG5：修改数量后小计未重算，待修复", strict=False)
def test_回归_改数量后小计与总额应更新(已登录购物车):
    """需求：改数量后，行小计与应付总额都要按 单价×数量 重算（BUG5）"""
    cart = 已登录购物车
    cart.open_index().add_to_cart("保温杯")            # 加购 1 件（49.90）
    cart.open().set_qty("保温杯", 3)                   # 改成 3 件 → 应为 149.70

    assert "149.70" in cart.row_text("保温杯"), f"行小计未更新：{cart.row_text('保温杯')}"
    assert "149.70" in cart.total_text, f"总额未更新：{cart.total_text}"


@pytest.mark.regression
def test_回归_多商品合计应正确(已登录购物车):
    """需求：总额 = 各商品 单价×数量 之和
    保温杯 49.90×2 + 数据线 19.90×1 = 119.70
    """
    cart = 已登录购物车
    cart.add_to_cart("保温杯", repeat=2).add_to_cart("数据线")   # PO 内部每次加购前回首页
    cart.open()
    assert "119.70" in cart.total_text, f"总额计算错误：{cart.total_text}"


@pytest.mark.regression
def test_回归_重复加购同一商品数量应累加(已登录购物车):
    """需求：同一商品重复加购 → 数量累加（1 → 2）"""
    cart = 已登录购物车
    cart.add_to_cart("数据线", repeat=2)                     # 连续加购 2 次
    cart.open()
    assert "39.80" in cart.row_text("数据线"), f"数量未累加：{cart.row_text('数据线')}"


@pytest.mark.regression
def test_回归_删除商品后购物车应为空(已登录购物车):
    """需求：删除后购物车回到空态，并提示可去逛逛"""
    cart = 已登录购物车
    cart.open_index().add_to_cart("数据线")
    cart.open().remove("数据线")
    assert cart.is_empty, f"删除后购物车不为空：{cart.page_text[:80]}"


# ---------- 结算 ----------


@pytest.mark.regression
def test_回归_空购物车应显示空态且无结算入口(已登录购物车):
    """需求：空购物车显示空态提示，不提供结算入口（避免用户误操作）"""
    cart = 已登录购物车
    cart.open()                                            # 打开空的购物车
    assert cart.is_empty, f"未显示空态提示：{cart.page_text[:80]}"
    assert cart.page.get_by_role("button", name="去结算").count() == 0, "空购物车不应出现结算按钮"


@pytest.mark.regression
def test_回归_结算成功后应显示下单金额(已登录购物车):
    """需求：结算成功页显示件数与应付金额"""
    cart = 已登录购物车
    cart.open_index().add_to_cart("数据线")            # 19.90
    cart.open().checkout()
    assert "下单成功" in cart.page_text, f"没进下单成功页：{cart.page_text[:80]}"
    assert "19.90" in cart.page_text, "下单页未显示正确金额"


# ---------- 库存边界 ----------

@pytest.mark.regression
@pytest.mark.xfail(reason="BUG6a：库存不足未拦截下单，待修复", strict=False)
def test_回归_超库存下单应被拒绝(已登录购物车):
    """需求（需求卡 C5）：库存不足时提示并拦截下单。显示器库存 5 → 买 6 件应被拒（BUG6a）"""
    cart = 已登录购物车
    stock = cart.stock_of("显示器")                    # 读当前库存（应为 5）
    cart.add_to_cart("显示器", repeat=stock + 1)      # 加购 库存+1 件（PO 内部会回首页）
    cart.open().checkout()
    assert "下单成功" not in cart.page_text, f"超库存竟然下单成功（库存 {stock}，买了 {stock + 1} 件）"

@pytest.mark.regression
@pytest.mark.xfail(reason="BUG6b：下单后库存未扣减，待修复", strict=False)
def test_回归_下单后库存应扣减(已登录购物车):
    """需求：下单成功后，商品库存应减少已购买数量（BUG6b）"""
    cart = 已登录购物车

    before = cart.stock_of("数据线")                   # 下单前库存
    cart.open_index().add_to_cart("数据线")            # 买 1 件
    cart.open().checkout()
    after = cart.stock_of("数据线")                    # 下单后再读库存
    assert after == before - 1, f"库存未扣减：下单前 {before}，下单后 {after}"

@pytest.mark.regression
@pytest.mark.xfail(reason="BUG7：数量 0 仍可下单，待修复", strict=False)
def test_回归_数量改为0不应允许下单(已登录购物车):
    cart = 已登录购物车
    cart.add_to_cart("数据线")  # 先加购
    cart.open().set_qty("数据线", 0)  # 用已有的 set_qty 方法把数量改成 0
    cart.checkout()  # 去结算
    assert "下单成功" not in cart.page_text, f"数量0居然下单成功"  # ← 你的断言 + 失败信息

