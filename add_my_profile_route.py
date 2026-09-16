# -*- coding: utf-8 -*-

content = open("web_app.py", encoding="utf-8").read()

# Проверяем что маршрутов нет
if "def my_profile" in content:
    print("my_profile already exists")
elif "def customer_profile" in content:
    print("customer_profile exists, adding only my_profile")

# Добавляем оба маршрута, если их нет

ROUTES = '''

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

'''

# Вставляем перед последней строкой с socketio или в самый конец перед __main__
markers = [
    '# ================= WEBSOCKET =================',
    '# ============ WEBSOCKET',
    '@socketio.on("connect")',
    "if __name__ == '__main__':",
]

inserted = False
for marker in markers:
    if marker in content:
        content = content.replace(marker, ROUTES + "\n" + marker, 1)
        print("Inserted before:", marker[:40])
        inserted = True
        break

if not inserted:
    if not content.endswith("\n"):
        content += "\n"
    content += ROUTES
    print("Appended to end")

open("web_app.py", "w", encoding="utf-8").write(content)

# Проверка методов БД
db_content = open("database.py", encoding="utf-8").read()
print()
print("Methods check:")
print("  get_customer_stats:", "def get_customer_stats" in db_content)
print("  get_customer_orders:", "def get_customer_orders" in db_content)
print("  get_customer_missions_progress:", "def get_customer_missions_progress" in db_content)

# Проверка шаблонов
import os
print()
print("Template check:")
print("  templates/customer_profile.html:", os.path.exists("templates/customer_profile.html"))
print("  templates/shop/my_profile.html:", os.path.exists("templates/shop/my_profile.html"))

# Проверка синтаксиса
import ast
try:
    ast.parse(open("web_app.py", encoding="utf-8").read())
    print()
    print("SYNTAX OK!")
except SyntaxError as e:
    print()
    print("SYNTAX ERROR at line", e.lineno, ":", e.msg)

print()
print("Done! Restart server.")