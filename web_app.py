from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, g, jsonify)
from flask_socketio import SocketIO, emit, join_room
from functools import wraps
from database import WarehouseDB
from auth import hash_password, verify_password
from config import Config
from notifications import NotificationCenter
from telegram_bot import TelegramBot

app = Flask(__name__, template_folder="templates")
app.secret_key = Config.SECRET_KEY
db = WarehouseDB()
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
telegram = TelegramBot(db)
notifier = NotificationCenter(db, socketio=socketio, telegram=telegram)


@app.before_request
def load_user():
    g.user = None
    g.customer = None
    if "user" in session:
        g.user = db.get_user(session["user"])
    if "customer_id" in session:
        g.customer = db.get_customer_by_id(session["customer_id"])


@app.context_processor
def inject_globals():
    return {
        "user": g.user,
        "customer": getattr(g, "customer", None),
    }


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.user:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.user or g.user["role"] != "admin":
            flash("Only admin", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper


def manager_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.user or g.user["role"] not in ("admin", "senior_seller", "mentor"):
            flash("Only managers", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper


def customer_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.customer:
            return redirect(url_for("shop_login"))
        return f(*args, **kwargs)
    return wrapper


ROLE_LABELS = {
    "admin": "Administrator",
    "senior_seller": "Senior Seller",
    "mentor": "Mentor",
    "seller": "Seller",
}


# ================= AUTH =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.get_user(username)
        if user and verify_password(password, user["password_hash"]):
            session["user"] = username
            return redirect(url_for("index"))
        flash("Wrong login or password", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        if db.get_user(username):
            flash("Username taken", "error")
        else:
            db.create_user(username, hash_password(password),
                           full_name, "seller")
            flash("Registered! Please login", "success")
            return redirect(url_for("login"))
    return render_template("register.html")


# ================= МОЙ СКЛАД =================
@app.route("/")
@login_required
def index():
    products = db.get_products(g.user["id"])
    total_value = sum(p["quantity"] * p["price"] for p in products)
    low_stock = len([p for p in products if p["quantity"] <= p["min_stock"]])
    return render_template("index.html", products=products,
                            total_value=total_value, low_stock=low_stock)


@app.route("/product/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        db.add_product(
            g.user["id"],
            request.form.get("name", "").strip(),
            request.form.get("category", "").strip(),
            int(request.form.get("quantity") or 0),
            float(request.form.get("price") or 0),
            int(request.form.get("min_stock") or 5))
        flash("Product added", "success")
        return redirect(url_for("index"))
    return render_template("product_form.html", product=None)


@app.route("/product/edit/<int:pid>", methods=["GET", "POST"])
@login_required
def edit_product(pid):
    product = db.get_product(pid, g.user["id"])
    if not product:
        flash("Not found", "error")
        return redirect(url_for("index"))
    if request.method == "POST":
        db.update_product(
            pid, g.user["id"],
            name=request.form.get("name", "").strip(),
            category=request.form.get("category", "").strip(),
            quantity=int(request.form.get("quantity") or 0),
            price=float(request.form.get("price") or 0),
            min_stock=int(request.form.get("min_stock") or 5))
        flash("Updated", "success")
        return redirect(url_for("index"))
    return render_template("product_form.html", product=product)


@app.route("/product/delete/<int:pid>", methods=["POST"])
@login_required
def delete_product(pid):
    db.delete_product(pid, g.user["id"])
    flash("Deleted", "success")
    return redirect(url_for("index"))


# ================= СОТРУДНИКИ =================
@app.route("/staff")
@login_required
@admin_required
def staff_list():
    users = db.list_users()
    return render_template("staff.html", users=users, role_labels=ROLE_LABELS)


@app.route("/staff/add", methods=["GET", "POST"])
@login_required
@admin_required
def staff_add():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        role = request.form.get("role", "seller")
        parent_id = request.form.get("parent_id") or None
        rate = float(request.form.get("commission_rate") or 0)

        if role not in ("senior_seller", "mentor", "seller", "accountant"):
            flash("Invalid role", "error")
            return redirect(url_for("staff_add"))

        if db.get_user(username):
            flash("Username already exists", "error")
            return redirect(url_for("staff_add"))

        if len(password) < 4:
            flash("Password too short (min 4)", "error")
            return redirect(url_for("staff_add"))

        db.create_user(username, hash_password(password), full_name, role,
                       parent_id=int(parent_id) if parent_id else None,
                       commission_rate=rate)
        flash("Employee added!", "success")
        return redirect(url_for("staff_list"))

    parents = db.list_users()
    return render_template("staff_form.html",
                            user=None, role_labels=ROLE_LABELS, parents=parents)


@app.route("/staff/edit/<int:uid>", methods=["GET", "POST"])
@login_required
@admin_required
def staff_edit(uid):
    user = db.get_user_by_id(uid)
    if not user:
        flash("User not found", "error")
        return redirect(url_for("staff_list"))

    if request.method == "POST":
        updates = {
            "full_name": request.form.get("full_name", "").strip(),
            "role": request.form.get("role", user["role"]),
            "commission_rate": float(request.form.get("commission_rate") or 0),
        }
        parent_id = request.form.get("parent_id") or None
        updates["parent_id"] = int(parent_id) if parent_id else None

        new_password = request.form.get("password", "").strip()
        if new_password:
            updates["password_hash"] = hash_password(new_password)

        db.update_user(uid, **updates)
        flash("Updated", "success")
        return redirect(url_for("staff_list"))

    parents = [u for u in db.list_users() if u["id"] != uid]
    return render_template("staff_form.html",
                            user=user, role_labels=ROLE_LABELS, parents=parents)


@app.route("/staff/delete/<int:uid>", methods=["POST"])
@login_required
@admin_required
def staff_delete(uid):
    if uid == g.user["id"]:
        flash("Cannot delete yourself", "error")
        return redirect(url_for("staff_list"))
    db.delete_user(uid)
    flash("Deleted", "success")
    return redirect(url_for("staff_list"))


# ================= КОМАНДА =================
@app.route("/team")
@login_required
@manager_required
def team():
    sub_ids = db.subordinates(g.user["id"])
    sub_users = [db.get_user_by_id(uid) for uid in sub_ids]
    sub_users = [u for u in sub_users if u]

    team_data = []
    for u in sub_users:
        products = db.get_products(u["id"])
        total_value = sum(p["quantity"] * p["price"] for p in products)
        team_data.append({
            "user": u,
            "products_count": len(products),
            "total_value": total_value,
        })

    return render_template("team.html", team=team_data,
                            role_labels=ROLE_LABELS)


@app.route("/team/member/<int:uid>")
@login_required
@manager_required
def team_member(uid):
    if uid not in db.visible_user_ids(g.user):
        flash("Access denied", "error")
        return redirect(url_for("team"))
    user = db.get_user_by_id(uid)
    products = db.get_products(uid)
    total_value = sum(p["quantity"] * p["price"] for p in products)
    return render_template("team_member.html", member=user,
                            products=products, total_value=total_value)


# ================= ЗАКАЗЫ =================
@app.route("/orders")
@login_required
def staff_orders():
    orders = db.get_orders()
    return render_template("staff_orders.html", orders=orders)


@app.route("/orders/<int:oid>")
@login_required
def staff_order_detail(oid):
    order = db.get_order(oid)
    if not order:
        flash("Not found", "error")
        return redirect(url_for("staff_orders"))
    messages = db.get_chat_messages(oid)
    return render_template("staff_order_detail.html",
                            order=order, messages=messages)


@app.route("/orders/<int:oid>/take", methods=["POST"])
@login_required
def order_take(oid):
    if db.take_order(oid, g.user["id"]):
        order = db.get_order(oid)
        socketio.emit("customer_notification", {
            "title": "Order #" + str(oid) + " taken",
            "body": "Staff: " + (g.user["full_name"] or g.user["username"])
        }, room="customer_" + str(order["customer_id"]))
        flash("Order taken", "success")
    else:
        flash("Already taken", "error")
    return redirect(url_for("staff_order_detail", oid=oid))






@app.route("/orders/<int:oid>/deliver-form")
@login_required
def order_deliver_form(oid):
    order = db.get_order(oid)
    if not order:
        flash("Заказ не найден", "error")
        return redirect("/orders")

    if order.get("taken_by") != g.user["id"]:
        flash("Это не ваш заказ", "error")
        return redirect("/orders")

    accounts = db.list_bank_accounts(active_only=True)
    my_products = db.get_products(g.user["id"])
    return render_template("order_deliver_form.html",
                            order=order, accounts=accounts,
                            my_products=my_products)


@app.route("/orders/<int:oid>/deliver", methods=["POST"])
@login_required
def order_deliver(oid):
    import json
    order = db.get_order(oid)
    if not order:
        flash("Заказ не найден", "error")
        return redirect("/orders")

    if order.get("taken_by") != g.user["id"]:
        flash("Это не ваш заказ", "error")
        return redirect("/orders")

    items_json = request.form.get("items_json", "[]")
    try:
        new_items = json.loads(items_json)
    except Exception:
        new_items = []

    if not new_items:
        flash("Добавьте хотя бы один товар", "error")
        return redirect("/orders/" + str(oid) + "/deliver-form")

    account_id = int(request.form.get("account_id") or 0)
    amount = float(request.form.get("amount") or 0)
    comment = request.form.get("comment", "").strip()

    if not account_id or amount <= 0:
        flash("Выберите счёт и укажите сумму", "error")
        return redirect("/orders/" + str(oid) + "/deliver-form")

    new_total = sum(it["price"] * it["quantity"] for it in new_items)

    old_items = order.get("items", [])
    old_total = order["total_amount"]
    changed = False
    if len(old_items) != len(new_items):
        changed = True
    else:
        for oi, ni in zip(old_items, new_items):
            if oi["product_name"] != ni["name"] or oi["quantity"] != ni["quantity"]:
                changed = True
                break

    db.update_order_items(oid, new_items, new_total)

    if changed:
        db.add_order_history(oid, "modified", "staff", g.user["id"],
                              g.user["full_name"] or g.user["username"],
                              "Заказ изменён. Было: " + str(round(old_total)) +
                              " RUB, стало: " + str(round(new_total)) + " RUB")

    with db.connect() as conn:
        conn.execute("""UPDATE orders SET status = 'delivered',
                        delivered_at = datetime('now'),
                        payment_status = 'pending',
                        paid_to_account_id = ?,
                        paid_amount = ?
                        WHERE id = ?""", (account_id, amount, oid))

    db.save_delivered_items(oid, [{
        "product_id": it.get("product_id"),
        "product_name": it["name"],
        "quantity_ordered": it["quantity"],
        "quantity_delivered": it["quantity"],
    } for it in new_items])

    db.create_transaction(
        account_id=account_id,
        ttype="income",
        amount=amount,
        order_id=oid,
        seller_id=g.user["id"],
        comment=comment or ("Поступление по заказу #" + str(oid)))

    if changed:
        socketio.emit("customer_notification", {
            "title": "Заказ #" + str(oid) + " изменён",
            "body": "Новая сумма: " + str(round(new_total)) + " RUB"
        }, room="customer_" + str(order["customer_id"]))
    else:
        socketio.emit("customer_notification", {
            "title": "Заказ #" + str(oid) + " доставлен",
            "body": "Спасибо за покупку!"
        }, room="customer_" + str(order["customer_id"]))

    with db.connect() as conn:
        staff = conn.execute("SELECT id FROM users WHERE role IN ('admin', 'accountant')").fetchall()
    for s in staff:
        msg = "Заказ #" + str(oid) + ": " + str(round(amount)) + " RUB"
        if changed:
            msg += " (изменён)"
        notifier.notify_user(s["id"], "Новое поступление", msg)

    flash("Заказ доставлен" + (" (изменён)" if changed else ""), "success")
    return redirect("/orders/" + str(oid))



@app.route("/orders/<int:oid>/chat", methods=["POST"])
@login_required
def staff_chat(oid):
    msg = request.form.get("message", "").strip()
    if msg:
        db.add_chat_message(oid, "staff",
                             g.user["full_name"] or g.user["username"], msg)
        socketio.emit("chat_message", {
            "order_id": oid,
            "sender_type": "staff",
            "sender_name": g.user["full_name"] or g.user["username"],
            "message": msg,
        }, room="order_" + str(oid))
    return redirect(url_for("staff_order_detail", oid=oid))


# ================= ПРОДАЖИ =================
@app.route("/sales")
@login_required
def sales_list():
    if g.user["role"] == "admin":
        sales = db.get_sales()
    else:
        sub_ids = db.visible_user_ids(g.user)
        sales = db.get_sales(seller_ids=sub_ids)
    return render_template("sales.html", sales=sales)


@app.route("/sales/new", methods=["GET", "POST"])
@login_required
def sale_new():
    products = db.get_products(g.user["id"])

    if request.method == "POST":
        pid = int(request.form.get("product_id") or 0)
        qty = int(request.form.get("quantity") or 0)
        actual = float(request.form.get("actual_amount") or 0)
        comment = request.form.get("comment", "").strip()

        product = db.get_product(pid, g.user["id"])
        if not product:
            flash("Product not found", "error")
            return redirect(url_for("sale_new"))

        if qty <= 0 or qty > product["quantity"]:
            flash("Not enough stock", "error")
            return redirect(url_for("sale_new"))

        rate = g.user.get("commission_rate") or 0
        expected = round(product["price"] * qty * (1 - rate / 100), 2)

        db.add_sale(g.user["id"], pid, product["name"], qty,
                    product["price"], rate, expected, actual, comment)

        db.update_product(pid, g.user["id"],
                          quantity=product["quantity"] - qty)

        flash("Sale sent for approval", "success")
        return redirect(url_for("sales_list"))

    return render_template("sale_new.html", products=products)


@app.route("/sales/<int:sid>/approve", methods=["POST"])
@login_required
@manager_required
def sale_approve(sid):
    db.approve_sale(sid, g.user["id"], approve=True)
    flash("Sale approved", "success")
    return redirect(url_for("sales_list"))


@app.route("/sales/<int:sid>/reject", methods=["POST"])
@login_required
@manager_required
def sale_reject(sid):
    sale = db.get_sale(sid)
    if not sale:
        flash("Not found", "error")
        return redirect(url_for("sales_list"))
    db.approve_sale(sid, g.user["id"], approve=False,
                    comment=request.form.get("comment", ""))
    product = db.get_product(sale["product_id"], sale["seller_id"])
    if product:
        db.update_product(product["id"], sale["seller_id"],
                          quantity=product["quantity"] + sale["quantity"])
    flash("Sale rejected, stock returned", "success")
    return redirect(url_for("sales_list"))


# ================= БРАК =================
@app.route("/defects")
@login_required
def defects_list():
    if g.user["role"] == "admin":
        defects = db.get_defects()
    else:
        sub_ids = db.visible_user_ids(g.user)
        defects = db.get_defects(seller_ids=sub_ids)
    return render_template("defects.html", defects=defects)


@app.route("/defects/new", methods=["GET", "POST"])
@login_required
def defect_new():
    products = db.get_products(g.user["id"])
    if request.method == "POST":
        pid = int(request.form.get("product_id") or 0)
        qty = int(request.form.get("quantity") or 0)
        reason = request.form.get("reason", "").strip()

        product = db.get_product(pid, g.user["id"])
        if not product or qty <= 0 or qty > product["quantity"]:
            flash("Invalid data", "error")
            return redirect(url_for("defect_new"))

        db.add_defect(g.user["id"], pid, product["name"], qty, reason)
        flash("Defect request sent", "success")
        return redirect(url_for("defects_list"))
    return render_template("defect_new.html", products=products)


@app.route("/defects/<int:did>/approve", methods=["POST"])
@login_required
@manager_required
def defect_approve(did):
    d = db.get_defect(did)
    if not d:
        flash("Not found", "error")
        return redirect(url_for("defects_list"))
    db.review_defect(did, g.user["id"], approve=True)
    product = db.get_product(d["product_id"], d["seller_id"])
    if product:
        new_qty = max(0, product["quantity"] - d["quantity"])
        db.update_product(product["id"], d["seller_id"], quantity=new_qty)
    flash("Defect approved", "success")
    return redirect(url_for("defects_list"))


@app.route("/defects/<int:did>/reject", methods=["POST"])
@login_required
@manager_required
def defect_reject(did):
    db.review_defect(did, g.user["id"], approve=False,
                     comment=request.form.get("comment", ""))
    flash("Defect rejected", "success")
    return redirect(url_for("defects_list"))


# ================= ПЕРЕМЕЩЕНИЯ =================
@app.route("/transfers")
@login_required
def transfers_list():
    if g.user["role"] == "admin":
        items = db.get_transfers()
    else:
        user_ids = db.visible_user_ids(g.user)
        items = db.get_transfers(user_ids=user_ids)
    return render_template("transfers.html", transfers=items)


@app.route("/transfers/new", methods=["GET", "POST"])
@login_required
def transfer_new():
    my_products = db.get_products(g.user["id"])
    visible = db.visible_user_ids(g.user)
    users = [db.get_user_by_id(uid) for uid in visible]
    users = [u for u in users if u and u["id"] != g.user["id"]]

    if request.method == "POST":
        to_id = int(request.form.get("to_user_id") or 0)
        pid = int(request.form.get("product_id") or 0)
        qty = int(request.form.get("quantity") or 0)
        comment = request.form.get("comment", "").strip()

        product = db.get_product(pid, g.user["id"])
        if not product or qty <= 0 or qty > product["quantity"]:
            flash("Invalid data", "error")
            return redirect(url_for("transfer_new"))

        requires_admin = 1 if g.user["role"] == "senior_seller" else 0

        db.add_transfer(g.user["id"], to_id, pid, product["name"], qty,
                        comment, g.user["id"], requires_admin)
        flash("Transfer created, waiting for approval", "success")
        return redirect(url_for("transfers_list"))

    return render_template("transfer_new.html",
                            products=my_products, users=users)


@app.route("/transfers/<int:tid>/approve", methods=["POST"])
@login_required
@manager_required
def transfer_approve(tid):
    t = db.get_transfer(tid)
    if not t:
        flash("Not found", "error")
        return redirect(url_for("transfers_list"))
    if t["requires_admin"] and g.user["role"] != "admin":
        flash("Only admin can approve this", "error")
        return redirect(url_for("transfers_list"))
    if db.approve_transfer(tid, g.user["id"]):
        flash("Transfer completed", "success")
    else:
        flash("Failed - not enough stock", "error")
    return redirect(url_for("transfers_list"))


@app.route("/transfers/<int:tid>/reject", methods=["POST"])
@login_required
@manager_required
def transfer_reject(tid):
    db.reject_transfer(tid, g.user["id"],
                       request.form.get("comment", ""))
    flash("Transfer rejected", "success")
    return redirect(url_for("transfers_list"))


# ================= РЕВИЗИИ =================
@app.route("/revisions")
@login_required
def revisions_list():
    if g.user["role"] == "admin":
        items = db.get_revisions()
    else:
        sub_ids = db.visible_user_ids(g.user)
        items = db.get_revisions(user_ids=sub_ids)
    return render_template("revisions.html", revisions=items)


@app.route("/revisions/new", methods=["GET", "POST"])
@login_required
@manager_required
def revision_new():
    sub_ids = db.subordinates(g.user["id"])
    targets = [db.get_user_by_id(uid) for uid in sub_ids]
    targets = [t for t in targets if t]

    if request.method == "POST":
        target_id = int(request.form.get("target_user_id") or 0)
        comment = request.form.get("comment", "").strip()
        db.create_revision(g.user["id"], target_id, comment)
        flash("Revision requested", "success")
        return redirect(url_for("revisions_list"))

    return render_template("revision_new.html", targets=targets)


@app.route("/revisions/<int:rid>", methods=["GET", "POST"])
@login_required
def revision_detail(rid):
    rev = db.get_revision(rid)
    if not rev:
        flash("Not found", "error")
        return redirect(url_for("revisions_list"))

    target = db.get_user_by_id(rev["target_user_id"])
    products = db.get_products(rev["target_user_id"])

    if request.method == "POST":
        total_diff = 0
        for p in products:
            key = "actual_" + str(p["id"])
            if key in request.form:
                try:
                    actual = int(request.form.get(key) or 0)
                except ValueError:
                    actual = p["quantity"]
                db.add_revision_item(rid, p["id"], p["name"],
                                     p["quantity"], actual)
                total_diff += actual - p["quantity"]
        db.complete_revision(rid, request.form.get("comment", ""))
        flash("Revision completed. Diff: " + str(total_diff), "success")
        return redirect(url_for("revisions_list"))

    items = db.get_revision_items(rid)
    return render_template("revision_detail.html",
                            revision=rev, target=target,
                            products=products, items=items)


# ================= ПРОФИЛЬ (Telegram) =================
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        if "generate_code" in request.form:
            import random
            code = str(random.randint(100000, 999999))
            db.update_user(g.user["id"], telegram_code=code)
            flash("Your code: " + code + " — send to bot: /link " + code,
                  "success")
        elif "unlink_telegram" in request.form:
            db.update_user(g.user["id"], telegram_id=None, telegram_code=None)
            flash("Telegram unlinked", "success")
        elif "save" in request.form:
            db.update_user(g.user["id"],
                           full_name=request.form.get("full_name", "").strip())
            flash("Saved", "success")
        return redirect(url_for("profile"))

    user = db.get_user_by_id(g.user["id"])
    return render_template("profile.html", profile_user=user)


# ================= БОНУСЫ =================
@app.route("/shop/bonus")
@customer_required
def customer_bonus():
    return render_template("shop/bonus.html", customer=g.customer)


# ================= МАГАЗИН =================
@app.route("/shop")
def shop_catalog():
    products = db.get_all_products()
    return render_template("shop/catalog.html", products=products)


@app.route("/shop/register", methods=["GET", "POST"])
def shop_register():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        name = request.form.get("name", "").strip()
        district = request.form.get("district", "").strip()
        if db.get_customer(phone):
            flash("Phone already registered", "error")
        else:
            db.create_customer(phone, hash_password(password), name, district)
            flash("Registered! Please login", "success")
            return redirect(url_for("shop_login"))
    return render_template("shop/register.html")


@app.route("/shop/login", methods=["GET", "POST"])
def shop_login():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        customer = db.get_customer(phone)
        if customer and verify_password(password, customer["password_hash"]):
            session["customer_id"] = customer["id"]
            return redirect(url_for("shop_catalog"))
        flash("Wrong phone or password", "error")
    return render_template("shop/login.html")


@app.route("/shop/logout")
def shop_logout():
    session.pop("customer_id", None)
    return redirect(url_for("shop_catalog"))




@app.route("/shop/product/<int:pid>")
def shop_product(pid):
    """Красивая карточка товара для покупателя"""
    product = db.get_product(pid)
    if not product:
        flash("Товар не найден", "error")
        return redirect("/shop")

    seller = db.get_user_by_id(product["owner_id"])
    rating = {"avg": 0, "count": 0}

    img = db.get_main_image(pid)
    if img:
        product["image"] = img.get("filename") if isinstance(img, dict) else img

    similar = []
    if product.get("category"):
        with db.connect() as conn:
            rows = conn.execute("""
                SELECT p.* FROM products p
                JOIN users u ON p.owner_id = u.id
                WHERE p.category = ? AND p.id != ? AND p.quantity > 0
                LIMIT 6
            """, (product["category"], pid)).fetchall()
            similar = [dict(r) for r in rows]
            for s in similar:
                si = db.get_main_image(s["id"])
                if si:
                    s["image"] = si.get("filename") if isinstance(si, dict) else si

    return render_template("shop/product_detail.html",
                            product=product,
                            seller=seller,
                            rating=rating,
                            similar=similar)


@app.route("/shop/cart/add/<int:pid>", methods=["POST"])
def cart_add(pid):
    qty = int(request.form.get("quantity") or 1)
    cart = session.get("cart", {})
    cart[str(pid)] = cart.get(str(pid), 0) + qty
    session["cart"] = cart
    session.modified = True
    flash("Added to cart", "success")
    return redirect(request.referrer or url_for("shop_catalog"))


@app.route("/shop/cart")
def cart_view():
    cart = session.get("cart", {})
    items = []
    total = 0
    for pid_str, qty in cart.items():
        p = db.get_product(int(pid_str))
        if p:
            subtotal = p["price"] * qty
            items.append({"product": p, "quantity": qty, "subtotal": subtotal})
            total += subtotal
    return render_template("shop/cart.html", items=items, total=total)


@app.route("/shop/checkout", methods=["POST"])
@customer_required
def shop_checkout():
    cart = session.get("cart", {})
    if not cart:
        flash("Cart empty", "error")
        return redirect(url_for("shop_catalog"))
    items = []
    for pid_str, qty in cart.items():
        p = db.get_product(int(pid_str))
        if p:
            items.append({
                "product_id": p["id"],
                "name": p["name"],
                "price": p["price"],
                "quantity": qty,
            })
    address = request.form.get("address", "").strip()
    comment = request.form.get("comment", "").strip()
    bonus_spent = int(request.form.get("bonus_spent") or 0)

    if bonus_spent > 0:
        if not db.spend_bonus(g.customer["id"], bonus_spent):
            bonus_spent = 0

    oid = db.create_order(g.customer["id"], items, address, comment,
                          bonus_spent)

    total = sum(i["price"] * i["quantity"] for i in items)
    for u in db.list_users():
        notifier.notify_user(u["id"], "New order #" + str(oid),
                              g.customer["name"] + ": " + str(round(total)) + " RUB")

    session.pop("cart", None)
    flash("Order #" + str(oid) + " placed!", "success")
    return redirect(url_for("shop_catalog"))


@app.route("/shop/my-orders")
@customer_required
def shop_my_orders():
    orders = db.get_orders(customer_id=g.customer["id"])
    for o in orders:
        full = db.get_order(o["id"])
        o["items"] = full.get("items", []) if full else []
    return render_template("shop/my_orders.html", orders=orders)


@app.route("/shop/orders/<int:oid>")
@customer_required
def shop_order_detail(oid):
    order = db.get_order(oid)
    if not order or order["customer_id"] != g.customer["id"]:
        flash("Not found", "error")
        return redirect(url_for("shop_my_orders"))
    messages = db.get_chat_messages(oid)
    return render_template("shop/order_detail.html",
                            order=order, messages=messages)


@app.route("/shop/orders/<int:oid>/chat", methods=["POST"])
@customer_required
def customer_chat(oid):
    order = db.get_order(oid)
    if not order or order["customer_id"] != g.customer["id"]:
        return jsonify({"error": "not found"}), 404
    msg = request.form.get("message", "").strip()
    if msg:
        db.add_chat_message(oid, "customer", g.customer["name"], msg)
        socketio.emit("chat_message", {
            "order_id": oid,
            "sender_type": "customer",
            "sender_name": g.customer["name"],
            "message": msg,
        }, room="order_" + str(oid))
        if order.get("taken_by"):
            socketio.emit("staff_notification", {
                "title": "Message from " + g.customer["name"],
                "body": msg[:80]
            }, room="user_" + str(order["taken_by"]))
    return redirect(url_for("shop_order_detail", oid=oid))


@app.route("/notifications")
@login_required
def notifications_page():
    notifs = db.get_notifications(g.user["id"])
    return render_template("notifications.html", notifications=notifs)




# ============== DASHBOARD ==============
@app.route('/dashboard')
@login_required
def dashboard():
    stats = db.dashboard_stats(30)
    top_p = db.top_products(30, 10)
    top_s = db.top_sellers(30, 10)
    return render_template('dashboard.html', stats=stats, top_products=top_p, top_sellers=top_s)


# ============== KPI ==============
@app.route('/kpi')
@login_required
def kpi_view():
    leaderboard = db.kpi_leaderboard(30)
    return render_template('kpi.html', leaderboard=leaderboard)


# ============== ZONES ==============
@app.route('/zones')
@login_required
def zones_list():
    zones = db.list_zones()
    return render_template('zones.html', zones=zones)


@app.route('/zones/add', methods=['POST'])
@login_required
def zone_add():
    name = request.form.get('name', '').strip()
    if name:
        db.add_zone(name, float(request.form.get('fee') or 0), float(request.form.get('free_from') or 0), int(request.form.get('eta') or 60))
        flash('Zone added', 'success')
    return redirect('/zones')


# ============== PRODUCT IMAGES ==============
@app.route('/product/<int:pid>/images', methods=['GET', 'POST'])
@login_required
def product_images(pid):
    product = db.get_product(pid, g.user['id'])
    if not product:
        flash('Not found', 'error')
        return redirect('/')
    if request.method == 'POST':
        f = request.files.get('image')
        if f and f.filename:
            import uuid
            upload_dir = 'static/uploads'
            os.makedirs(upload_dir, exist_ok=True)
            ext = f.filename.rsplit('.', 1)[-1].lower()
            name = uuid.uuid4().hex[:12] + '.' + ext
            f.save(os.path.join(upload_dir, name))
            db.add_product_image(pid, name)
            flash('Image uploaded', 'success')
        return redirect('/product/' + str(pid) + '/images')
    images = db.list_product_images(pid)
    return render_template('product_images.html', product=product, images=images)



@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory('static/uploads', filename)




# ==================== MISSIONS CONSTRUCTOR ====================

@app.route("/missions")
@login_required
@admin_required
def admin_missions_list():
    missions = db.list_missions_admin()
    pending = db.get_pending_missions()
    return render_template("admin_missions.html",
                            missions=missions, pending=pending)


@app.route("/missions/new", methods=["GET", "POST"])
@login_required
@admin_required
def admin_mission_create():
    if request.method == "POST":
        code = request.form.get("code", "").strip().lower().replace(" ", "_")
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        icon = request.form.get("icon", "🎯").strip() or "🎯"
        category = request.form.get("mission_category", "buy")
        target = int(request.form.get("target_value") or 1)
        reward = int(request.form.get("reward_value") or 0)
        action_url = request.form.get("action_url", "").strip()
        platform = request.form.get("platform", "").strip()
        verify_hint = request.form.get("verify_hint", "").strip()
        repeat = request.form.get("repeat_type", "once")
        requires_approval = 1 if request.form.get("requires_approval") else 0

        if not code or not title or reward <= 0:
            flash("Заполните код, название и награду", "error")
            return redirect("/missions/new")

        # Проверяем уникальность кода
        existing = db.get_mission_by_code(code)
        if existing:
            code = code + "_" + str(int(__import__("time").time()))

        mid = db.create_mission_full(
            code=code, title=title, description=description, icon=icon,
            mission_category=category, target_value=target,
            reward_value=reward, action_url=action_url, platform=platform,
            verify_hint=verify_hint, repeat_type=repeat,
            requires_approval=requires_approval)

        flash("Миссия создана!", "success")
        return redirect("/missions")

    return render_template("admin_mission_form.html", mission=None)


@app.route("/missions/<int:mid>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def admin_mission_edit(mid):
    m = db.get_mission(mid)
    if not m:
        flash("Миссия не найдена", "error")
        return redirect("/missions")

    if request.method == "POST":
        with db.connect() as conn:
            conn.execute("""UPDATE missions SET
                title=?, description=?, icon=?, mission_category=?,
                target_value=?, reward_value=?, action_url=?, platform=?,
                verify_hint=?, repeat_type=?, requires_approval=?
                WHERE id=?""",
                (request.form.get("title", "").strip(),
                 request.form.get("description", "").strip(),
                 request.form.get("icon", "🎯").strip() or "🎯",
                 request.form.get("mission_category", "buy"),
                 int(request.form.get("target_value") or 1),
                 int(request.form.get("reward_value") or 0),
                 request.form.get("action_url", "").strip(),
                 request.form.get("platform", "").strip(),
                 request.form.get("verify_hint", "").strip(),
                 request.form.get("repeat_type", "once"),
                 1 if request.form.get("requires_approval") else 0,
                 mid))
        flash("Миссия обновлена", "success")
        return redirect("/missions")

    return render_template("admin_mission_form.html", mission=m)


@app.route("/missions/<int:mid>/delete", methods=["POST"])
@login_required
@admin_required
def admin_mission_delete(mid):
    with db.connect() as conn:
        conn.execute("DELETE FROM missions WHERE id=?", (mid,))
        conn.execute("DELETE FROM customer_mission_progress WHERE mission_id=?", (mid,))
    flash("Миссия удалена", "success")
    return redirect("/missions")


@app.route("/missions/<int:mid>/toggle", methods=["POST"])
@login_required
@admin_required
def admin_mission_toggle(mid):
    with db.connect() as conn:
        conn.execute("UPDATE missions SET is_active = 1 - is_active WHERE id=?", (mid,))
    flash("Статус изменён", "success")
    return redirect("/missions")


@app.route("/missions/approve/<int:progress_id>", methods=["POST"])
@login_required
@admin_required
def admin_mission_approve(progress_id):
    approve = request.form.get("approve") == "1"
    db.approve_mission_customer(progress_id, approve)
    flash("Одобрено" if approve else "Отклонено", "success")
    return redirect("/missions")


# ==================== MISSIONS FOR CUSTOMERS ====================

@app.route("/shop/missions")
@customer_required
def shop_missions():
    missions = db.get_visible_missions(g.customer["id"])
    return render_template("shop/missions.html", missions=missions)


@app.route("/shop/missions/<int:mid>/start", methods=["POST"])
@customer_required
def shop_mission_start(mid):
    db.start_mission(g.customer["id"], mid)
    flash("Миссия начата!", "success")
    return redirect("/shop/missions")


@app.route("/shop/missions/<int:mid>/complete", methods=["POST"])
@customer_required
def shop_mission_complete(mid):
    proof_text = request.form.get("proof_text", "").strip()
    proof_url = request.form.get("proof_url", "").strip()
    db.complete_mission_customer(g.customer["id"], mid, proof_text, proof_url)
    flash("Отправлено на проверку! Ожидайте подтверждения.", "success")
    return redirect("/shop/missions")



@app.route("/customer/<int:cid>")
@login_required
def customer_profile(cid):
    """Профиль покупателя для админа/сотрудников"""
    customer = db.get_customer_by_id(cid)
    if not customer:
        flash("Покупатель не найден", "error")
        return redirect("/")
    stats = db.get_customer_stats(cid)
    orders = db.get_customer_orders(cid, limit=30)
    missions = db.get_customer_missions_progress(cid)
    return render_template("customer_profile.html",
                            customer=customer,
                            stats=stats,
                            orders=orders,
                            missions=missions)


@app.route("/shop/profile")
@customer_required
def my_profile():
    """Мой профиль для покупателя"""
    cid = g.customer["id"]
    stats = db.get_customer_stats(cid)
    orders = db.get_customer_orders(cid, limit=30)
    missions = db.get_customer_missions_progress(cid)
    return render_template("shop/my_profile.html",
                            customer=g.customer,
                            stats=stats,
                            orders=orders,
                            missions=missions)


# ================= WEBSOCKET =================


# ==================== FINANCE ====================

def accountant_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.user or g.user["role"] not in ("admin", "accountant"):
            flash("Доступ только для админа и бухгалтера", "error")
            return redirect("/")
        return f(*args, **kwargs)
    return wrapper


@app.route("/admin/bank-accounts", methods=["GET", "POST"])
@login_required
@admin_required
def admin_bank_accounts():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            name = request.form.get("name", "").strip()
            if name:
                db.create_bank_account(
                    name=name,
                    bank=request.form.get("bank", "").strip(),
                    account_number=request.form.get("account_number", "").strip())
                flash("Счёт добавлен", "success")
        elif action == "update":
            aid = int(request.form.get("aid"))
            db.update_bank_account(aid,
                name=request.form.get("name", "").strip(),
                bank=request.form.get("bank", "").strip(),
                account_number=request.form.get("account_number", "").strip(),
                is_active=1 if request.form.get("is_active") else 0)
            flash("Счёт обновлён", "success")
        elif action == "delete":
            aid = int(request.form.get("aid"))
            result = db.delete_bank_account(aid)
            flash("Счёт удалён" if result == "deleted" else "Счёт отключён (есть транзакции)",
                  "success")
        return redirect("/admin/bank-accounts")

    accounts = db.list_bank_accounts()
    total = db.get_total_balance()
    return render_template("admin_bank_accounts.html",
                            accounts=accounts, total=total)


@app.route("/finance")
@login_required
@accountant_required
def finance_home():
    stats = db.get_finance_stats()
    dashboard = db.get_finance_dashboard_stats(30)
    accounts = db.list_bank_accounts(active_only=True)
    pending = db.list_transactions(status="pending", limit=20)
    recent_income = db.list_transactions(status="approved", ttype="income", limit=10)
    recent_expense = db.list_transactions(status="approved", ttype="expense", limit=10)
    return render_template("finance_home.html",
                            stats=stats,
                            dashboard=dashboard,
                            accounts=accounts,
                            pending=pending,
                            recent_income=recent_income,
                            recent_expense=recent_expense,
                            is_admin=(g.user["role"] == "admin"))


@app.route("/finance/transactions")
@login_required
@accountant_required
def finance_transactions():
    ttype = request.args.get("type")
    status = request.args.get("status")
    txs = db.list_transactions(status=status, ttype=ttype, limit=300)
    return render_template("finance_transactions.html",
                            transactions=txs, current_type=ttype, current_status=status)


@app.route("/finance/transaction/<int:tid>", methods=["GET", "POST"])
@login_required
@accountant_required
def finance_transaction_detail(tid):
    tx = db.get_transaction(tid)
    if not tx:
        flash("Транзакция не найдена", "error")
        return redirect("/finance")

    if request.method == "POST":
        approve = request.form.get("approve") == "1"
        comment = request.form.get("comment", "").strip()
        if db.approve_transaction(tid, g.user["id"], approve, comment):
            flash("Одобрено" if approve else "Отклонено", "success")
        else:
            flash("Не удалось обработать", "error")
        return redirect("/finance")

    return render_template("finance_transaction_detail.html", tx=tx)


@app.route("/finance/new-expense", methods=["GET", "POST"])
@login_required
@accountant_required
def finance_new_expense():
    accounts = db.list_bank_accounts(active_only=True)

    if request.method == "POST":
        account_id = int(request.form.get("account_id"))
        amount = float(request.form.get("amount") or 0)
        comment = request.form.get("comment", "").strip()

        if not account_id or amount <= 0:
            flash("Заполните счёт и сумму", "error")
            return redirect("/finance/new-expense")

        tid = db.create_transaction(
            account_id=account_id,
            ttype="expense",
            amount=amount,
            requester_id=g.user["id"],
            comment=comment)
        flash("Заявка создана. Ждёт подтверждения бухгалтера.", "success")
        return redirect("/finance")

    return render_template("finance_new_expense.html", accounts=accounts)


@socketio.on("connect")
def ws_connect():
    if session.get("user"):
        u = db.get_user(session["user"])
        if u:
            join_room("user_" + str(u["id"]))
    if session.get("customer_id"):
        join_room("customer_" + str(session["customer_id"]))


@socketio.on("join_order")
def ws_join_order(data):
    oid = data.get("order_id")
    if oid:
        join_room("order_" + str(oid))


# ============== СТАРТ ==============
telegram.start()

if __name__ == "__main__":
    print()
    print("=" * 50)
    print("Server started!")
    print("=" * 50)
    print()
    print("Staff:   http://localhost:5000/login")
    print("Login:   admin / admin123")
    print()
    print("Shop:    http://localhost:5000/shop")
    print()
    print("Press Ctrl+C to stop")
    print()
    socketio.run(app, debug=False, host="0.0.0.0", port=5000,
                 allow_unsafe_werkzeug=True)