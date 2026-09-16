# -*- coding: utf-8 -*-
import os

print("Adding finance routes to web_app.py...")

ROUTES = '''

# ==================== BANK ACCOUNTS ====================

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


# ==================== FINANCE ====================

@app.route("/finance")
@login_required
@accountant_required
def finance_home():
    stats = db.get_finance_stats()
    accounts = db.list_bank_accounts(active_only=True)
    pending = db.list_transactions(status="pending", limit=100)
    return render_template("finance_home.html",
                            stats=stats, accounts=accounts, pending=pending)


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
'''

content = open("web_app.py", encoding="utf-8").read()

if "def finance_home" not in content:
    marker = "# ================= WEBSOCKET ================="
    if marker in content:
        content = content.replace(marker, ROUTES + "\n" + marker)
        open("web_app.py", "w", encoding="utf-8").write(content)
        print("OK: finance routes added")
    else:
        print("ERROR: marker not found")
else:
    print("already exists")

# Проверка
import ast
try:
    ast.parse(open("web_app.py", encoding="utf-8").read())
    print("SYNTAX OK")
except SyntaxError as e:
    print("SYNTAX ERROR at", e.lineno, ":", e.msg)

# ============================================================
# ШАБЛОНЫ
# ============================================================
print()
print("Creating templates...")


# ============ Управление счетами ============
ADMIN_ACCOUNTS = '''{% extends "base.html" %}{% block content %}
<h1>💳 Банковские счета</h1>

<div class="stats">
  <div class="stat-box">
    <h3>Всего счетов</h3>
    <div class="value">{{ accounts|length }}</div>
  </div>
  <div class="stat-box" style="background:linear-gradient(135deg,#27ae60,#16a085);color:#fff">
    <h3 style="color:rgba(255,255,255,.8)">ОБЩИЙ БАЛАНС</h3>
    <div class="value" style="color:#fff">{{ "%.2f"|format(total) }} ₽</div>
  </div>
</div>

<div class="card">
  <h3>➕ Добавить счёт</h3>
  <form method="post" style="display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:12px;margin-top:12px">
    <input type="hidden" name="action" value="create">
    <input name="name" placeholder="Название (Сбербанк)" required style="margin:0">
    <input name="bank" placeholder="Банк (sberbank)" style="margin:0">
    <input name="account_number" placeholder="Номер счёта" style="margin:0">
    <button class="btn btn-success" type="submit">Добавить</button>
  </form>
</div>

<div class="card">
  <h3>Все счета</h3>
  <table style="margin-top:12px">
    <thead><tr>
      <th>Название</th><th>Банк</th><th>Номер</th>
      <th>Баланс</th><th>Активен</th><th>Действия</th>
    </tr></thead>
    <tbody>
    {% for a in accounts %}
    <tr>
      <td><b>{{ a.name }}</b></td>
      <td>{{ a.bank or '-' }}</td>
      <td style="font-family:monospace;font-size:13px">{{ a.account_number or '-' }}</td>
      <td><b style="color:{% if a.balance > 0 %}#27ae60{% elif a.balance < 0 %}#e74c3c{% else %}#7f8c8d{% endif %};font-size:16px">
        {{ "%.2f"|format(a.balance) }} ₽
      </b></td>
      <td>{% if a.is_active %}✅{% else %}🚫{% endif %}</td>
      <td>
        <details style="display:inline-block">
          <summary style="cursor:pointer" class="btn btn-sm">✏️</summary>
          <div style="position:absolute;background:#fff;padding:16px;border:1px solid #ddd;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.15);z-index:100;margin-top:8px">
            <form method="post" style="display:grid;gap:8px;min-width:280px">
              <input type="hidden" name="action" value="update">
              <input type="hidden" name="aid" value="{{ a.id }}">
              <input name="name" value="{{ a.name }}" required>
              <input name="bank" value="{{ a.bank or '' }}">
              <input name="account_number" value="{{ a.account_number or '' }}">
              <label><input type="checkbox" name="is_active" {% if a.is_active %}checked{% endif %}> Активен</label>
              <button class="btn btn-sm btn-success">Сохранить</button>
            </form>
          </div>
        </details>
        <form method="post" style="display:inline" onsubmit="return confirm('Удалить счёт?')">
          <input type="hidden" name="action" value="delete">
          <input type="hidden" name="aid" value="{{ a.id }}">
          <button class="btn btn-sm btn-danger">🗑️</button>
        </form>
      </td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
</div>

{% endblock %}'''

with open("templates/admin_bank_accounts.html", "w", encoding="utf-8") as f:
    f.write(ADMIN_ACCOUNTS)
print("OK admin_bank_accounts.html")


# ============ Финансовая панель ============
FINANCE_HOME = '''{% extends "base.html" %}{% block content %}
<h1>💰 Финансы</h1>

<div class="stats">
  <div class="stat-box" style="background:linear-gradient(135deg,#2c3e50,#34495e);color:#fff">
    <h3 style="color:rgba(255,255,255,.8)">ОБЩИЙ БАЛАНС</h3>
    <div class="value" style="color:#fff">{{ "%.2f"|format(stats.total) }} ₽</div>
  </div>
  <div class="stat-box" style="background:linear-gradient(135deg,#27ae60,#16a085);color:#fff">
    <h3 style="color:rgba(255,255,255,.8)">ПОСТУПИЛО</h3>
    <div class="value" style="color:#fff">+{{ "%.2f"|format(stats.income) }} ₽</div>
  </div>
  <div class="stat-box" style="background:linear-gradient(135deg,#e74c3c,#c0392b);color:#fff">
    <h3 style="color:rgba(255,255,255,.8)">УШЛО</h3>
    <div class="value" style="color:#fff">-{{ "%.2f"|format(stats.expense) }} ₽</div>
  </div>
  <div class="stat-box">
    <h3>Ожидают</h3>
    <div class="value" style="color:#f39c12">{{ stats.pending_count }}</div>
  </div>
</div>

<div class="card">
  <h3>💳 Счета компании</h3>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:16px">
    {% for a in accounts %}
    <div style="background:#fff;border:2px solid #ecf0f1;border-radius:12px;padding:20px">
      <div style="font-size:14px;color:#7f8c8d">{{ a.bank or 'счёт' }}</div>
      <div style="font-size:20px;font-weight:800;margin:4px 0">{{ a.name }}</div>
      <div style="font-size:12px;color:#95a5a6;font-family:monospace">{{ a.account_number or '' }}</div>
      <div style="font-size:28px;font-weight:900;color:{% if a.balance > 0 %}#27ae60{% else %}#e74c3c{% endif %};margin-top:12px">
        {{ "%.2f"|format(a.balance) }} ₽
      </div>
    </div>
    {% endfor %}
  </div>
</div>

{% if pending %}
<div class="card" style="border-left:4px solid #f39c12">
  <h3>⏳ Ожидают подтверждения ({{ pending|length }})</h3>
  <table style="margin-top:12px">
    <thead><tr>
      <th>Дата</th><th>Тип</th><th>Кто</th>
      <th>Счёт</th><th>Сумма</th><th>Комментарий</th><th></th>
    </tr></thead>
    <tbody>
    {% for t in pending %}
    <tr>
      <td style="font-size:12px">{{ t.created_at }}</td>
      <td>
        {% if t.type == 'income' %}📥 Поступление
        {% else %}📤 Расход{% endif %}
      </td>
      <td>
        {% if t.seller_name %}{{ t.seller_name }}{% endif %}
        {% if t.requester_name %}{{ t.requester_name }}{% endif %}
        {% if t.order_id %}<br><small>Заказ #{{ t.order_id }}</small>{% endif %}
      </td>
      <td>{{ t.account_name }}</td>
      <td><b style="color:{% if t.type == 'income' %}#27ae60{% else %}#e74c3c{% endif %}">
        {% if t.type == 'income' %}+{% else %}-{% endif %}{{ "%.2f"|format(t.amount) }} ₽
      </b></td>
      <td style="font-size:12px">{{ t.comment or '-' }}</td>
      <td>
        <a href="/finance/transaction/{{ t.id }}" class="btn btn-sm">Открыть</a>
      </td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
</div>
{% endif %}

<div class="card">
  <a href="/finance/transactions" class="btn">📊 Вся история транзакций</a>
  <a href="/finance/new-expense" class="btn btn-red">📤 Создать заявку на расход</a>
</div>

{% endblock %}'''

with open("templates/finance_home.html", "w", encoding="utf-8") as f:
    f.write(FINANCE_HOME)
print("OK finance_home.html")


# ============ История транзакций ============
FINANCE_TXS = '''{% extends "base.html" %}{% block content %}
<h1>📊 История транзакций</h1>

<div class="card">
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    <a href="/finance/transactions" class="btn btn-sm {% if not current_type and not current_status %}btn-success{% endif %}">Все</a>
    <a href="/finance/transactions?type=income" class="btn btn-sm {% if current_type == 'income' %}btn-success{% endif %}">📥 Поступления</a>
    <a href="/finance/transactions?type=expense" class="btn btn-sm {% if current_type == 'expense' %}btn-success{% endif %}">📤 Расходы</a>
    <a href="/finance/transactions?status=pending" class="btn btn-sm {% if current_status == 'pending' %}btn-success{% endif %}">⏳ Ожидают</a>
    <a href="/finance/transactions?status=approved" class="btn btn-sm {% if current_status == 'approved' %}btn-success{% endif %}">✅ Одобрено</a>
    <a href="/finance/transactions?status=rejected" class="btn btn-sm {% if current_status == 'rejected' %}btn-success{% endif %}">❌ Отклонено</a>
  </div>
</div>

<div class="card">
  <table>
    <thead><tr>
      <th>Дата</th><th>Тип</th><th>Счёт</th><th>Сумма</th>
      <th>Статус</th><th>Кто</th><th>Комментарий</th><th></th>
    </tr></thead>
    <tbody>
    {% for t in transactions %}
    <tr>
      <td style="font-size:12px">{{ t.created_at }}</td>
      <td>
        {% if t.type == 'income' %}📥{% else %}📤{% endif %}
        {{ t.type }}
      </td>
      <td>{{ t.account_name }}</td>
      <td><b style="color:{% if t.type == 'income' %}#27ae60{% else %}#e74c3c{% endif %}">
        {% if t.type == 'income' %}+{% else %}-{% endif %}{{ "%.2f"|format(t.amount) }} ₽
      </b></td>
      <td>
        {% if t.status == 'pending' %}⏳
        {% elif t.status == 'approved' %}✅
        {% else %}❌{% endif %}
        {{ t.status }}
      </td>
      <td style="font-size:12px">
        {{ t.seller_name or t.requester_name or '-' }}
        {% if t.order_id %}<br>Заказ #{{ t.order_id }}{% endif %}
      </td>
      <td style="font-size:12px">{{ t.comment or '-' }}</td>
      <td><a href="/finance/transaction/{{ t.id }}" class="btn btn-sm">Открыть</a></td>
    </tr>
    {% else %}
    <tr><td colspan="8" style="text-align:center;padding:20px">Нет транзакций</td></tr>
    {% endfor %}
    </tbody>
  </table>
</div>

<a href="/finance" class="btn">← Назад</a>

{% endblock %}'''

with open("templates/finance_transactions.html", "w", encoding="utf-8") as f:
    f.write(FINANCE_TXS)
print("OK finance_transactions.html")


# ============ Детали транзакции ============
FINANCE_TX_DETAIL = '''{% extends "base.html" %}{% block content %}
<h1>💳 Транзакция #{{ tx.id }}</h1>

<div class="card">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
    <div>
      <h3>Информация</h3>
      <p><b>Дата:</b> {{ tx.created_at }}</p>
      <p><b>Тип:</b>
        {% if tx.type == 'income' %}📥 Поступление
        {% else %}📤 Расход{% endif %}
      </p>
      <p><b>Счёт:</b> {{ tx.account_name }}</p>
      <p><b>Сумма:</b>
        <span style="font-size:22px;font-weight:900;color:{% if tx.type == 'income' %}#27ae60{% else %}#e74c3c{% endif %}">
          {% if tx.type == 'income' %}+{% else %}-{% endif %}{{ "%.2f"|format(tx.amount) }} ₽
        </span>
      </p>
      {% if tx.seller_name %}<p><b>Продавец:</b> {{ tx.seller_name }}</p>{% endif %}
      {% if tx.order_id %}<p><b>Заказ:</b> <a href="/orders/{{ tx.order_id }}">#{{ tx.order_id }}</a></p>{% endif %}
      {% if tx.comment %}<p><b>Комментарий:</b> {{ tx.comment }}</p>{% endif %}
    </div>
    <div>
      <h3>Статус</h3>
      <div style="font-size:24px;font-weight:900;color:{% if tx.status == 'pending' %}#f39c12{% elif tx.status == 'approved' %}#27ae60{% else %}#e74c3c{% endif %}">
        {% if tx.status == 'pending' %}⏳ Ожидает
        {% elif tx.status == 'approved' %}✅ Одобрено
        {% else %}❌ Отклонено{% endif %}
      </div>
      {% if tx.reviewed_at %}
      <p style="margin-top:12px;font-size:13px;color:#7f8c8d">
        Обработано: {{ tx.reviewed_at }}
      </p>
      {% endif %}
    </div>
  </div>
</div>

{% if tx.status == 'pending' %}
<div class="card">
  <h3>Действия</h3>
  <form method="post">
    <label>Комментарий (опционально)</label>
    <textarea name="comment" rows="2"></textarea>
    <div style="display:flex;gap:12px;margin-top:12px">
      <button name="approve" value="1" class="btn btn-success" type="submit">
        ✅ Подтвердить
      </button>
      <button name="approve" value="0" class="btn btn-danger" type="submit">
        ❌ Отклонить
      </button>
    </div>
  </form>
</div>
{% endif %}

<a href="/finance" class="btn">← Назад</a>

{% endblock %}'''

with open("templates/finance_transaction_detail.html", "w", encoding="utf-8") as f:
    f.write(FINANCE_TX_DETAIL)
print("OK finance_transaction_detail.html")


# ============ Новая заявка на расход ============
FINANCE_NEW_EXPENSE = '''{% extends "base.html" %}{% block content %}
<h1>📤 Заявка на расход</h1>

<div class="card" style="max-width:600px">
  <form method="post">
    <label>Со счёта *</label>
    <select name="account_id" required>
      <option value="">— выберите счёт —</option>
      {% for a in accounts %}
      <option value="{{ a.id }}">{{ a.name }} ({{ "%.2f"|format(a.balance) }} ₽)</option>
      {% endfor %}
    </select>

    <label>Сумма (₽) *</label>
    <input name="amount" type="number" step="0.01" min="0.01" required>

    <label>Комментарий (за что / кому)</label>
    <textarea name="comment" rows="3" placeholder="Оплата поставщику за товар"></textarea>

    <div style="display:flex;gap:12px;margin-top:16px">
      <button class="btn btn-red" type="submit">📤 Отправить заявку</button>
      <a href="/finance" class="btn" style="background:#95a5a6">Отмена</a>
    </div>

    <p style="margin-top:12px;font-size:13px;color:#7f8c8d">
      Заявка будет ждать подтверждения. Деньги спишутся только после одобрения.
    </p>
  </form>
</div>

{% endblock %}'''

with open("templates/finance_new_expense.html", "w", encoding="utf-8") as f:
    f.write(FINANCE_NEW_EXPENSE)
print("OK finance_new_expense.html")

print()
print("=" * 50)
print("DONE!")
print("=" * 50)
print()
print("Now add:")
print("  - Role 'accountant' to Employees dropdown")
print("  - Menu links in base.html")
print()