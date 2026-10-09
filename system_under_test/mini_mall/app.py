# -*- coding: utf-8 -*-
"""
迷你商城 MiniMall —— 软件测试练习靶场（被测系统，故意埋有缺陷）
===========================================================
技术栈: Flask + SQLite（sqlite3 标准库）+ Jinja2 模板
运行:   python app.py   →  http://127.0.0.1:5001

角色分工（请记住，这是被测对象不是你的作品）:
  - 页面(前端模板)  : templates/*.html  用户看到和操作的东西
  - 后端(路由逻辑)  : app.py            接收请求、处理业务、读写数据库
  - 数据库          : mall.db           users / products / carts 三张表

⚠️ 本系统故意按"真实但粗糙的开发"方式编写，存在若干缺陷（BUG），
   作为你 s1d08/s1d09 的测试对象。请以测试工程师视角使用它。
"""
import sqlite3
from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, g)

app = Flask(__name__)
app.secret_key = "mini-mall-demo-secret"          # 演示用；真实系统绝不硬编码
DB = "mall.db"
ADMIN_PHONE = "13800000000"


# ---------- 数据库 ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB)
    db.executescript("""
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS carts;
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            descr TEXT DEFAULT ''
        );
        CREATE TABLE carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            qty INTEGER NOT NULL DEFAULT 1,
            subtotal REAL NOT NULL DEFAULT 0
        );
        INSERT INTO products (name, price, stock, descr) VALUES
            ('测试专用保温杯', 49.9, 50, '304 不锈钢 500ml'),
            ('测试专用机械键盘', 299.0, 10, '青轴 87 键'),
            ('测试专用显示器', 899.0, 5, '27 寸 2K'),
            ('测试专用数据线', 19.9, 100, 'Type-C 快充 1.5m');
    """)
    db.commit()
    db.close()


# ---------- 工具 ----------
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    row = get_db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    return row


@app.context_processor
def inject_user():
    return {"user": current_user()}


# ---------- 页面 ----------
@app.route("/")
def index():
    items = get_db().execute("SELECT * FROM products").fetchall()
    return render_template("index.html", items=items)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        phone = (request.form.get("phone") or "").strip()
        pwd = request.form.get("password") or ""
        pwd2 = request.form.get("password2") or ""
        db = get_db()
        # 需求：手机号须为 11 位数字；密码至少 8 位且同时包含字母和数字；注册成功自动登录进首页
        if len(pwd) < 8:                                    # BUG2 位置：只查长度，漏"含字母和数字"
            flash("密码长度至少 8 位")
            return render_template("register.html")
        if pwd != pwd2:
            flash("两次密码不一致")
            return render_template("register.html")
        if db.execute("SELECT id FROM users WHERE phone=?", (phone,)).fetchone():
            flash("该手机号已注册")
            return render_template("register.html")
        db.execute("INSERT INTO users (phone, password) VALUES (?,?)", (phone, pwd))
        db.commit()
        # BUG3 位置：需求是"注册成功自动登录进入首页"，这里却跳去登录页
        flash("注册成功，请登录")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = (request.form.get("phone") or "").strip()
        pwd = request.form.get("password") or ""
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
        # BUG4 位置：需求要求统一提示"手机号或密码错误"，这里区分了两种文案 → 泄露账号是否存在
        if row is None:
            flash("该账号不存在")
            return render_template("login.html")
        if row["password"] != pwd:
            flash("密码错误")
            return render_template("login.html")
        session["user_id"] = row["id"]
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/cart/add", methods=["POST"])
def cart_add():
    if not current_user():
        flash("请先登录")
        return redirect(url_for("login"))
    pid = int(request.form.get("product_id"))
    db = get_db()
    item = db.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    if item is None:
        flash("商品不存在")
        return redirect(url_for("index"))
    uid = session["user_id"]
    row = db.execute("SELECT * FROM carts WHERE user_id=? AND product_id=?",
                     (uid, pid)).fetchone()
    if row:
        db.execute("UPDATE carts SET qty=qty+1, subtotal=? WHERE id=?",
                   (round(item["price"] * (row["qty"] + 1), 2), row["id"]))
    else:
        db.execute("INSERT INTO carts (user_id, product_id, qty, subtotal) VALUES (?,?,1,?)",
                   (uid, pid, round(item["price"], 2)))
    db.commit()
    return redirect(url_for("cart"))


@app.route("/cart/update", methods=["POST"])
def cart_update():
    if not current_user():
        return redirect(url_for("login"))
    cid = int(request.form.get("cart_id"))
    qty = int(request.form.get("qty") or 1)
    db = get_db()
    row = db.execute("SELECT c.*, p.price FROM carts c JOIN products p ON p.id=c.product_id "
                     "WHERE c.id=? AND c.user_id=?", (cid, session["user_id"])).fetchone()
    if row is None:
        flash("购物车条目不存在")
        return redirect(url_for("cart"))
    # BUG5 位置：数量更新了，但 subtotal（行小计快照）没有重算 → 数量变了金额不变
    db.execute("UPDATE carts SET qty=? WHERE id=?", (qty, cid))
    db.commit()
    return redirect(url_for("cart"))


@app.route("/cart/remove", methods=["POST"])
def cart_remove():
    if not current_user():
        return redirect(url_for("login"))
    cid = int(request.form.get("cart_id"))
    db = get_db()
    db.execute("DELETE FROM carts WHERE id=? AND user_id=?", (cid, session["user_id"]))
    db.commit()
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    if not current_user():
        flash("请先登录")
        return redirect(url_for("login"))
    uid = session["user_id"]
    rows = get_db().execute(
        "SELECT c.id, c.product_id, c.qty, c.subtotal, p.name, p.price, p.stock "
        "FROM carts c JOIN products p ON p.id=c.product_id WHERE c.user_id=?",
        (uid,)).fetchall()
    total = round(sum(r["subtotal"] for r in rows), 2)
    return render_template("cart.html", rows=rows, total=total)


@app.route("/checkout", methods=["POST"])
def checkout():
    if not current_user():
        return redirect(url_for("login"))
    uid = session["user_id"]
    db = get_db()
    rows = db.execute(
        "SELECT c.product_id, c.qty, p.price, p.name, p.stock FROM carts c "
        "JOIN products p ON p.id=c.product_id WHERE c.user_id=?", (uid,)).fetchall()
    if not rows:
        flash("购物车是空的")
        return redirect(url_for("cart"))
    # BUG6 位置：需求是"库存不足时提示并拦截下单"，这里完全没有检查库存 → 超库存也能下单成功
    total = round(sum(r["price"] * r["qty"] for r in rows), 2)
    db.execute("DELETE FROM carts WHERE user_id=?", (uid,))
    db.commit()
    return render_template("checkout.html", total=total, count=sum(r["qty"] for r in rows))


if __name__ == "__main__":
    init_db()
    print("迷你商城已启动: http://127.0.0.1:5001")
    app.run(host="127.0.0.1", port=5001, debug=False)
