# -*- coding: utf-8 -*-
import os

print("1. Adding statistics method to database.py...")

content = open("database.py", encoding="utf-8").read()

METHODS = '''

    def get_finance_dashboard_stats(self, days=30):
        """Статистика для дашборда админа"""
        from datetime import datetime, timedelta
        with self.connect() as conn:
            # Всего
            total = conn.execute("SELECT COALESCE(SUM(balance), 0) FROM bank_accounts WHERE is_active = 1").fetchone()[0] or 0

            # За период
            r = conn.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN type='income' AND status='approved' THEN amount ELSE 0 END), 0) as income,
                    COALESCE(SUM(CASE WHEN type='expense' AND status='approved' THEN amount ELSE 0 END), 0) as expense,
                    COUNT(CASE WHEN status='pending' THEN 1 END) as pending
                FROM transactions
                WHERE created_at >= DATE('now', ?)
            """, (f'-{days} days',)).fetchone()

            # По дням за последние 7 дней
            by_day = [dict(r) for r in conn.execute("""
                SELECT DATE(created_at) as day,
                       SUM(CASE WHEN type='income' AND status='approved' THEN amount ELSE 0 END) as income,
                       SUM(CASE WHEN type='expense' AND status='approved' THEN amount ELSE 0 END) as expense
                FROM transactions
                WHERE created_at >= DATE('now', '-7 days')
                GROUP BY day ORDER BY day
            """).fetchall()]

            return {
                "total": total,
                "income": r["income"] if r else 0,
                "expense": r["expense"] if r else 0,
                "pending": r["pending"] if r else 0,
                "by_day": by_day,
            }
'''

if "def get_finance_dashboard_stats" not in content:
    if not content.endswith("\n"):
        content += "\n"
    content += METHODS
    open("database.py", "w", encoding="utf-8").write(content)
    print("   OK method added")
else:
    print("   already exists")


print()
print("2. Updating /finance route...")

web = open("web_app.py", encoding="utf-8").read()

OLD = '''@app.route("/finance")
@login_required
@accountant_required
def finance_home():
    stats = db.get_finance_stats()
    accounts = db.list_bank_accounts(active_only=True)
    pending = db.list_transactions(status="pending", limit=100)
    return render_template("finance_home.html",
                            stats=stats, accounts=accounts, pending=pending)'''

NEW = '''@app.route("/finance")
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
                            is_admin=(g.user["role"] == "admin"))'''

if OLD in web:
    web = web.replace(OLD, NEW)
    open("web_app.py", "w", encoding="utf-8").write(web)
    print("   OK finance_home updated")
else:
    print("   WARN: pattern not found")


print()
print("3. Creating admin finance dashboard template...")

FINANCE_HOME = '''{% extends "base.html" %}{% block content %}

<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:24px">
  <h1 style="margin:0">💰 Финансы</h1>
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    {% if is_admin %}
      <a href="/admin/bank-accounts" class="btn">💳 Управление счетами</a>
      <a href="/finance/new-expense" class="btn btn-red">📤 Новая заявка</a>
    {% endif %}
  </div>
</div>

{# ============ ОСНОВНЫЕ ЦИФРЫ ============ #}
<div class="stats">
  <div class="stat-box" style="background:linear-gradient(135deg,#2c3e50,#34495e);color:#fff">
    <h3 style="color:rgba(255,255,255,.8)">ОБЩИЙ БАЛАНС</h3>
    <div class="value" style="color:#fff">{{ "%.2f"|format(dashboard.total) }} ₽</div>
  </div>
  <div class="stat-box" style="background:linear-gradient(135deg,#27ae60,#16a085);color:#fff">
    <h3 style="color:rgba(255,255,255,.8)">ПОСТУПИЛО (30 дней)</h3>
    <div class="value" style="color:#fff">+{{ "%.0f"|format(dashboard.income) }} ₽</div>
  </div>
  <div class="stat-box" style="background:linear-gradient(135deg,#e74c3c,#c0392b);color:#fff">
    <h3 style="color:rgba(255,255,255,.8)">УШЛО (30 дней)</h3>
    <div class="value" style="color:#fff">−{{ "%.0f"|format(dashboard.expense) }} ₽</div>
  </div>
  <div class="stat-box" style="background:linear-gradient(135deg,#f39c12,#e67e22);color:#fff">
    <h3 style="color:rgba(255,255,255,.8)">ОЖИДАЮТ</h3>
    <div class="value" style="color:#fff">{{ dashboard.pending }}</div>
  </div>
</div>

{# ============ СЧЕТА ============ #}
<div class="card">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h3 style="margin:0">💳 Счета компании</h3>
    {% if is_admin %}
      <a href="/admin/bank-accounts" class="btn btn-sm">Управление →</a>
    {% endif %}
  </div>

  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:16px">
    {% for a in accounts %}
    <div style="background:#fff;border:2px solid #ecf0f1;border-radius:14px;padding:20px;transition:all .3s"
         onmouseover="this.style.borderColor='#7c3aed';this.style.transform='translateY(-3px)'"
         onmouseout="this.style.borderColor='#ecf0f1';this.style.transform=''">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div>
          <div style="font-size:12px;color:#7f8c8d;text-transform:uppercase;letter-spacing:1px">
            {{ a.bank or 'счёт' }}
          </div>
          <div style="font-size:20px;font-weight:800;margin:4px 0">{{ a.name }}</div>
        </div>
        <div style="font-size:28px">💳</div>
      </div>
      <div style="font-family:monospace;font-size:11px;color:#95a5a6;margin-top:4px">
        {{ a.account_number or '—' }}
      </div>
      <div style="font-size:30px;font-weight:900;color:{% if a.balance > 0 %}#27ae60{% elif a.balance < 0 %}#e74c3c{% else %}#7f8c8d{% endif %};margin-top:14px;letter-spacing:-1px">
        {{ "%.2f"|format(a.balance) }} ₽
      </div>
    </div>
    {% endfor %}
  </div>
</div>

{# ============ СТАТИСТИКА ПО ДНЯМ ============ #}
{% if dashboard.by_day %}
<div class="card">
  <h3>📊 Статистика за 7 дней</h3>
  <div style="margin-top:16px">
    {% set max_val = 1 %}
    {% for d in dashboard.by_day %}
      {% if d.income and d.income > max_val %}{% set _ = max_val.__class__ %}{% endif %}
    {% endfor %}
    
    <table>
      <thead><tr>
        <th>Дата</th><th>Поступление</th><th>Расход</th><th>Итого за день</th>
      </tr></thead>
      <tbody>
      {% for d in dashboard.by_day %}
      {% set day_total = (d.income or 0) - (d.expense or 0) %}
      <tr>
        <td style="font-size:13px">{{ d.day }}</td>
        <td style="color:#27ae60;font-weight:700">+{{ "%.2f"|format(d.income or 0) }} ₽</td>
        <td style="color:#e74c3c;font-weight:700">−{{ "%.2f"|format(d.expense or 0) }} ₽</td>
        <td>
          <b style="color:{% if day_total >= 0 %}#27ae60{% else %}#e74c3c{% endif %}">
            {% if day_total > 0 %}+{% endif %}{{ "%.2f"|format(day_total) }} ₽
          </b>
        </td>
      </tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endif %}

{# ============ ОЖИДАЮТ ПОДТВЕРЖДЕНИЯ ============ #}
{% if pending %}
<div class="card" style="border-left:4px solid #f39c12">
  <h3>⏳ Ожидают подтверждения ({{ pending|length }})</h3>
  <table style="margin-top:12px">
    <thead><tr>
      <th>Дата</th><th>Тип</th><th>Кто</th>
      <th>Счёт</th><th>Сумма</th><th></th>
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
        {{ t.seller_name or t.requester_name or '—' }}
        {% if t.order_id %}<br><small>Заказ #{{ t.order_id }}</small>{% endif %}
      </td>
      <td>{{ t.account_name }}</td>
      <td><b style="color:{% if t.type == 'income' %}#27ae60{% else %}#e74c3c{% endif %};font-size:16px">
        {% if t.type == 'income' %}+{% else %}−{% endif %}{{ "%.2f"|format(t.amount) }} ₽
      </b></td>
      <td>
        <a href="/finance/transaction/{{ t.id }}" class="btn btn-sm btn-warning">Обработать</a>
      </td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
</div>
{% endif %}

{# ============ ПОСЛЕДНИЕ ПОСТУПЛЕНИЯ ============ #}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
  <div class="card">
    <h3>📥 Последние поступления</h3>
    {% if recent_income %}
    <table style="margin-top:12px">
      <thead><tr><th>Дата</th><th>От кого</th><th>Сумма</th></tr></thead>
      <tbody>
      {% for t in recent_income %}
      <tr>
        <td style="font-size:12px">{{ t.created_at[:16] }}</td>
        <td style="font-size:13px">{{ t.seller_name or t.requester_name or '—' }}</td>
        <td style="color:#27ae60;font-weight:700">+{{ "%.2f"|format(t.amount) }} ₽</td>
      </tr>
      {% endfor %}
      </tbody>
    </table>
    <a href="/finance/transactions?type=income" class="btn btn-sm" style="margin-top:12px">Все поступления →</a>
    {% else %}
    <p style="text-align:center;color:#7f8c8d;padding:20px">Поступлений нет</p>
    {% endif %}
  </div>

  <div class="card">
    <h3>📤 Последние расходы</h3>
    {% if recent_expense %}
    <table style="margin-top:12px">
      <thead><tr><th>Дата</th><th>Кому</th><th>Сумма</th></tr></thead>
      <tbody>
      {% for t in recent_expense %}
      <tr>
        <td style="font-size:12px">{{ t.created_at[:16] }}</td>
        <td style="font-size:13px">{{ t.comment[:40] if t.comment else '—' }}</td>
        <td style="color:#e74c3c;font-weight:700">−{{ "%.2f"|format(t.amount) }} ₽</td>
      </tr>
      {% endfor %}
      </tbody>
    </table>
    <a href="/finance/transactions?type=expense" class="btn btn-sm" style="margin-top:12px">Все расходы →</a>
    {% else %}
    <p style="text-align:center;color:#7f8c8d;padding:20px">Расходов нет</p>
    {% endif %}
  </div>
</div>

<div class="card" style="text-align:center">
  <a href="/finance/transactions" class="btn">📊 Полная история транзакций</a>
</div>

{% endblock %}'''

with open("templates/finance_home.html", "w", encoding="utf-8") as f:
    f.write(FINANCE_HOME)
print("   OK finance_home.html updated")

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
print("=" * 50)
print("DONE!")
print("=" * 50)
print()
print("Теперь /finance показывает:")
print("  💰 Общий баланс + статистика")
print("  💳 Все счета с балансами")
print("  📊 Таблица за 7 дней")
print("  ⏳ Ожидающие транзакции")
print("  📥 Последние поступления")
print("  📤 Последние расходы")
print()
print("Restart server.")