# -*- coding: utf-8 -*-
import os

print("1. Adding DB method to modify orders...")

content = open("database.py", encoding="utf-8").read()

METHODS = '''

    # ================= ORDER MODIFICATION =================
    def update_order_items(self, order_id, new_items, new_total):
        """Заменяет состав заказа и пересчитывает итог"""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            # Удаляем старые позиции
            c.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
            # Добавляем новые
            for it in new_items:
                subtotal = it["price"] * it["quantity"]
                c.execute("""INSERT INTO order_items
                    (order_id, product_id, product_name, product_price,
                     quantity, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (order_id, it.get("product_id"), it["name"],
                     it["price"], it["quantity"], subtotal))
            # Обновляем сумму заказа
            c.execute("""UPDATE orders SET total_amount = ?, updated_at = ?
                         WHERE id = ?""", (new_total, now, order_id))

    def add_order_history(self, order_id, action, actor_type, actor_id,
                           actor_name, comment=""):
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            conn.execute("""INSERT INTO order_history
                (order_id, action, actor_type, actor_id, actor_name, comment, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (order_id, action, actor_type, actor_id, actor_name, comment, now))
'''

if "def update_order_items" not in content:
    if not content.endswith("\n"):
        content += "\n"
    content += METHODS
    open("database.py", "w", encoding="utf-8").write(content)
    print("   OK methods added")
else:
    print("   already exists")


print()
print("2. Replacing order_deliver route...")

web = open("web_app.py", encoding="utf-8").read()

# Находим существующий order_deliver и заменяем
import re
pattern = r'@app\.route\("/orders/<int:oid>/deliver", methods=\["POST"\]\)\s*\n@login_required\s*\ndef order_deliver\(oid\):.*?(?=\n\n@app\.route)'
match = re.search(pattern, web, re.DOTALL)

NEW_DELIVER = '''@app.route("/orders/<int:oid>/deliver", methods=["POST"])
@login_required
def order_deliver(oid):
    order = db.get_order(oid)
    if not order:
        flash("Заказ не найден", "error")
        return redirect("/orders")

    if order.get("taken_by") != g.user["id"]:
        flash("Это не ваш заказ", "error")
        return redirect("/orders")

    # Парсим новые позиции заказа из формы
    # Формат: items[] = JSON массив
    import json
    items_json = request.form.get("items_json", "[]")
    try:
        new_items = json.loads(items_json)
    except Exception:
        new_items = []

    if not new_items:
        flash("Добавьте хотя бы один товар в заказ", "error")
        return redirect("/orders/" + str(oid) + "/deliver-form")

    # Проверяем счёт и сумму
    account_id = int(request.form.get("account_id") or 0)
    amount = float(request.form.get("amount") or 0)
    comment = request.form.get("comment", "").strip()

    if not account_id or amount <= 0:
        flash("Выберите счёт и укажите сумму", "error")
        return redirect("/orders/" + str(oid) + "/deliver-form")

    # Считаем новую сумму
    new_total = sum(it["price"] * it["quantity"] for it in new_items)

    # Проверяем изменился ли состав
    old_items = order.get("items", [])
    old_total = order["total_amount"]
    changed = False
    if len(old_items) != len(new_items):
        changed = True
    else:
        for old_i, new_i in zip(old_items, new_items):
            if (old_i["product_name"] != new_i["name"] or
                old_i["quantity"] != new_i["quantity"]):
                changed = True
                break

    # Обновляем состав заказа
    db.update_order_items(oid, new_items, new_total)

    # Добавляем в историю
    if changed:
        db.add_order_history(oid, "modified", "staff", g.user["id"],
                              g.user["full_name"] or g.user["username"],
                              "Заказ изменён продавцом. Было: " +
                              str(round(old_total)) + " ₽, стало: " +
                              str(round(new_total)) + " ₽")

    # Помечаем заказ доставленным
    with db.connect() as conn:
        conn.execute("""UPDATE orders SET status = 'delivered',
                        delivered_at = datetime('now'),
                        payment_status = 'pending',
                        paid_to_account_id = ?,
                        paid_amount = ?
                        WHERE id = ?""", (account_id, amount, oid))

    # Сохраняем доставленные товары (для истории)
    db.save_delivered_items(oid, [{
        "product_id": it.get("product_id"),
        "product_name": it["name"],
        "quantity_ordered": it["quantity"],
        "quantity_delivered": it["quantity"],
    } for it in new_items])

    # Создаём транзакцию для бухгалтера
    tid = db.create_transaction(
        account_id=account_id,
        ttype="income",
        amount=amount,
        order_id=oid,
        seller_id=g.user["id"],
        comment=comment or ("Поступление по заказу #" + str(oid)))

    # Уведомляем покупателя
    if changed:
        socketio.emit("customer_notification", {
            "title": "Заказ #" + str(oid) + " изменён",
            "body": "Новая сумма: " + str(round(new_total)) + " ₽"
        }, room="customer_" + str(order["customer_id"]))
    else:
        socketio.emit("customer_notification", {
            "title": "Заказ #" + str(oid) + " доставлен",
            "body": "Спасибо за покупку!"
        }, room="customer_" + str(order["customer_id"]))

    # Уведомляем админов и бухгалтеров
    with db.connect() as conn:
        staff = conn.execute("""SELECT id FROM users
                                WHERE role IN ('admin', 'accountant')""").fetchall()
    for s in staff:
        msg = "Заказ #" + str(oid) + ": " + str(round(amount)) + " ₽"
        if changed:
            msg += " (изменён с " + str(round(old_total)) + " ₽)"
        notifier.notify_user(s["id"], "💰 Новое поступление", msg)

    if changed:
        flash("✓ Заказ изменён и доставлен. Покупатель уведомлён.", "success")
    else:
        flash("✓ Заказ доставлен. Ожидает подтверждения бухгалтера.", "success")

    return redirect("/orders/" + str(oid))'''

if match:
    web = web[:match.start()] + NEW_DELIVER + web[match.end():]
    print("   OK: order_deliver replaced")
else:
    print("   WARN: not found")


print()
print("3. Updating order_deliver_form route...")

# Обновляем форму — теперь она передаёт товары продавца для добавления
OLD_FORM = '''@app.route("/orders/<int:oid>/deliver-form")
@login_required
def order_deliver_form(oid):
    """Страница выбора счёта и товаров при доставке"""
    order = db.get_order(oid)
    if not order:
        flash("Заказ не найден", "error")
        return redirect("/orders")

    if order.get("taken_by") != g.user["id"]:
        flash("Это не ваш заказ", "error")
        return redirect("/orders")

    accounts = db.list_bank_accounts(active_only=True)
    return render_template("order_deliver_form.html",
                            order=order, accounts=accounts)'''

NEW_FORM = '''@app.route("/orders/<int:oid>/deliver-form")
@login_required
def order_deliver_form(oid):
    """Страница выбора счёта и товаров при доставке"""
    order = db.get_order(oid)
    if not order:
        flash("Заказ не найден", "error")
        return redirect("/orders")

    if order.get("taken_by") != g.user["id"]:
        flash("Это не ваш заказ", "error")
        return redirect("/orders")

    accounts = db.list_bank_accounts(active_only=True)
    # Товары продавца (для замены)
    my_products = db.get_products(g.user["id"])

    return render_template("order_deliver_form.html",
                            order=order, accounts=accounts,
                            my_products=my_products)'''

if OLD_FORM in web:
    web = web.replace(OLD_FORM, NEW_FORM)
    print("   OK: deliver_form updated")
elif "my_products = db.get_products" in web:
    print("   already updated")
else:
    print("   WARN: form route not found")

open("web_app.py", "w", encoding="utf-8").write(web)


print()
print("4. Syntax check...")
import ast
try:
    ast.parse(open("web_app.py", encoding="utf-8").read())
    print("   web_app.py OK")
    ast.parse(open("database.py", encoding="utf-8").read())
    print("   database.py OK")
except SyntaxError as e:
    print("   ERROR:", e.lineno, e.msg)

print()
print("5. Creating new order_deliver_form.html template...")

TEMPLATE = '''{% extends "base.html" %}{% block content %}
<h1>📦 Доставка заказа #{{ order.id }}</h1>

<div class="card" style="background:linear-gradient(135deg,#f8f9fa,#fff);border-left:4px solid #3498db">
  <p><b>Клиент:</b> {{ order.customer_name }} · {{ order.customer_phone }}</p>
  <p><b>Адрес:</b> {{ order.address or '—' }}</p>
  <p><b>Статус:</b> {{ order.status }}</p>
</div>

<form method="post" action="/orders/{{ order.id }}/deliver" id="deliverForm">
  <input type="hidden" name="items_json" id="itemsJson" value="">

  <div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
      <h3 style="margin:0">🛒 Состав заказа</h3>
      <button type="button" class="btn btn-warning" onclick="showAddProduct()">
        ➕ Добавить товар
      </button>
    </div>

    <p style="color:#7f8c8d;font-size:13px;margin-top:8px">
      Если покупатель заменил товары — измените состав. Покупателю придёт уведомление.
    </p>

    <table id="itemsTable" style="margin-top:16px">
      <thead><tr>
        <th>Товар</th>
        <th>Цена</th>
        <th>Кол-во</th>
        <th>Сумма</th>
        <th></th>
      </tr></thead>
      <tbody id="itemsBody">
      {# Существующие товары #}
      {% for it in order['items'] %}
      <tr data-product-id="{{ it.product_id or '' }}"
          data-name="{{ it.product_name }}"
          data-price="{{ it.product_price }}">
        <td><b>{{ it.product_name }}</b></td>
        <td>{{ "%.2f"|format(it.product_price) }} ₽</td>
        <td>
          <input type="number" class="qty-input" value="{{ it.quantity }}"
                 min="1" style="width:80px;padding:6px;margin:0">
        </td>
        <td class="subtotal">{{ "%.2f"|format(it.subtotal) }} ₽</td>
        <td>
          <button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)">✕</button>
        </td>
      </tr>
      {% endfor %}
      </tbody>
      <tfoot>
        <tr style="background:#f8f9fa">
          <td colspan="3" style="text-align:right;font-weight:700">ИТОГО:</td>
          <td colspan="2" id="totalSum" style="font-weight:900;font-size:20px;color:#ed1d36">0.00 ₽</td>
        </tr>
      </tfoot>
    </table>
  </div>

  <div class="card" style="border-left:4px solid #f39c12">
    <h3>💳 Куда поступили деньги?</h3>

    <label>Счёт для зачисления *</label>
    <select name="account_id" required>
      <option value="">— выберите счёт —</option>
      {% for a in accounts %}
      <option value="{{ a.id }}">{{ a.name }}{% if a.account_number and a.account_number != '-' %} ({{ a.account_number }}){% endif %}</option>
      {% endfor %}
    </select>

    <label>Сумма поступления (₽) *</label>
    <input type="number" name="amount" id="amountInput" step="0.01" min="0.01"
           required style="font-size:20px;font-weight:700">

    <label>Комментарий (опционально)</label>
    <textarea name="comment" rows="2" placeholder="Например: оплата наличными"></textarea>

    <div style="background:#fff3cd;padding:12px;border-radius:8px;margin-top:16px;font-size:13px">
      ⚠️ После подтверждения создаётся заявка на поступление. Бухгалтер проверит и зачислит деньги.
    </div>
  </div>

  <div style="display:flex;gap:12px">
    <button class="btn btn-success" type="submit" style="flex:1;padding:18px;font-size:17px"
            onclick="return prepareSubmit()">
      ✅ Подтвердить доставку
    </button>
    <a href="/orders/{{ order.id }}" class="btn" style="background:#95a5a6">Отмена</a>
  </div>
</form>

{# ========== Модальное окно "Добавить товар" ========== #}
<div id="addModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;align-items:center;justify-content:center">
  <div style="background:#fff;border-radius:12px;padding:24px;max-width:600px;width:90%;max-height:80vh;overflow-y:auto">
    <h3>➕ Добавить товар в заказ</h3>
    <p style="color:#7f8c8d;font-size:13px">Выберите товар из своего склада</p>

    <div id="productList" style="margin-top:16px">
      {% for p in my_products %}
      {% if p.quantity > 0 %}
      <div style="padding:12px;border:1px solid #e5e5ea;border-radius:8px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center">
        <div>
          <b>{{ p.name }}</b>
          <div style="font-size:12px;color:#7f8c8d">{{ "%.2f"|format(p.price) }} ₽ · в наличии {{ p.quantity }}</div>
        </div>
        <button type="button" class="btn btn-sm btn-success"
                onclick="addProductRow({{ p.id }}, '{{ p.name|replace("'", "\\'") }}', {{ p.price }}, {{ p.quantity }})">
          Добавить
        </button>
      </div>
      {% endif %}
      {% endfor %}
    </div>

    <button type="button" class="btn" style="background:#95a5a6;margin-top:16px;width:100%"
            onclick="hideAddProduct()">Закрыть</button>
  </div>
</div>

<script>
function recalcTotal(){
  var total = 0;
  document.querySelectorAll('#itemsBody tr').forEach(function(row){
    var price = parseFloat(row.dataset.price) || 0;
    var qty = parseInt(row.querySelector('.qty-input').value) || 0;
    var subtotal = price * qty;
    row.querySelector('.subtotal').textContent = subtotal.toFixed(2) + ' ₽';
    total += subtotal;
  });
  document.getElementById('totalSum').textContent = total.toFixed(2) + ' ₽';
  var amount = document.getElementById('amountInput');
  if(!amount.dataset.touched) amount.value = total.toFixed(2);
}

function toggleQty(btn){}

function removeRow(btn){
  btn.closest('tr').remove();
  recalcTotal();
}

function showAddProduct(){
  document.getElementById('addModal').style.display = 'flex';
}
function hideAddProduct(){
  document.getElementById('addModal').style.display = 'none';
}

function addProductRow(pid, name, price, maxQty){
  var html = '<tr data-product-id="' + pid + '" data-name="' + name + '" data-price="' + price + '">' +
    '<td><b>' + name + '</b></td>' +
    '<td>' + price.toFixed(2) + ' ₽</td>' +
    '<td><input type="number" class="qty-input" value="1" min="1" max="' + maxQty + '" style="width:80px;padding:6px;margin:0"></td>' +
    '<td class="subtotal">0.00 ₽</td>' +
    '<td><button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)">✕</button></td>' +
    '</tr>';
  document.getElementById('itemsBody').insertAdjacentHTML('beforeend', html);
  hideAddProduct();
  recalcTotal();
}

function prepareSubmit(){
  var items = [];
  document.querySelectorAll('#itemsBody tr').forEach(function(row){
    var price = parseFloat(row.dataset.price) || 0;
    var qty = parseInt(row.querySelector('.qty-input').value) || 0;
    if(qty > 0){
      items.push({
        product_id: row.dataset.productId || null,
        name: row.dataset.name,
        price: price,
        quantity: qty
      });
    }
  });
  if(items.length === 0){
    alert('Добавьте хотя бы один товар');
    return false;
  }
  document.getElementById('itemsJson').value = JSON.stringify(items);
  return true;
}

// Слушаем изменения количества
document.addEventListener('input', function(e){
  if(e.target.classList.contains('qty-input')) recalcTotal();
});

// Считаем при загрузке
recalcTotal();
document.getElementById('amountInput').addEventListener('input', function(){
  this.dataset.touched = '1';
});
</script>

{% endblock %}'''

with open("templates/order_deliver_form.html", "w", encoding="utf-8") as f:
    f.write(TEMPLATE)
print("   OK order_deliver_form.html")

print()
print("=" * 50)
print("DONE!")
print("=" * 50)
print()
print("Что нового:")
print("  • Продавец может УДАЛИТЬ товар из заказа")
print("  • Может ДОБАВИТЬ товар со своего склада")
print("  • Сумма пересчитывается автоматически")
print("  • Покупателю приходит уведомление об изменении")
print("  • Заказ обновляется в БД")
print()
print("Restart server.")