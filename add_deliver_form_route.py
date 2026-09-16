# -*- coding: utf-8 -*-
import re

content = open("web_app.py", encoding="utf-8").read()

if "def order_deliver_form" in content:
    print("Route already exists")
    exit()

# Маршруты: форма доставки + обновлённый order_deliver
NEW_ROUTES = '''

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


'''

# Удаляем старый order_deliver
old_pattern = r'@app\.route\("/orders/<int:oid>/deliver", methods=\["POST"\]\)\s*\n@login_required\s*\ndef order_deliver\(oid\):.*?(?=\n\n@app\.route)'
m = re.search(old_pattern, content, re.DOTALL)
if m:
    content = content[:m.start()] + content[m.end():]
    print("Removed old order_deliver")

# Вставляем новые маршруты после order_take
marker = "@app.route(\"/orders/<int:oid>/deliver-form\")"
if marker not in content:
    # Найдём конец order_take (по следующему @app.route)
    take_idx = content.find("def order_take(oid):")
    if take_idx == -1:
        print("ERROR: order_take not found")
        exit()
    # Ищем следующий @app.route после order_take
    next_route = content.find("\n@app.route", take_idx)
    if next_route == -1:
        print("ERROR: next route not found")
        exit()
    content = content[:next_route] + "\n" + NEW_ROUTES + content[next_route:]
    print("Inserted new routes after order_take")

open("web_app.py", "w", encoding="utf-8").write(content)

# Проверка
c = open("web_app.py", encoding="utf-8").read()
print()
print("Check:")
print("  order_deliver_form:", "def order_deliver_form" in c)
print("  order_deliver:", c.count("def order_deliver("))
print("  deliver-form route:", "/deliver-form" in c)

import ast
try:
    ast.parse(c)
    print("SYNTAX OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e.lineno, e.msg)

print()
print("Done! Restart server.")