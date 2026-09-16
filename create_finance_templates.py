# -*- coding: utf-8 -*-
import os

print("Creating finance templates...")

# ============ 1. Управление счетами ============
T1 = '''{% extends "base.html" %}{% block content %}
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

<a href="/finance" class="btn">← К финансам</a>
{% endblock %}'''

with open("templates/admin_bank_accounts.html", "w", encoding="utf-8") as f:
    f.write(T1)
print("OK admin_bank_accounts.html")


# ============ 2. История транзакций ============
T2 = '''{% extends "base.html" %}{% block content %}
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
      <td>{% if t.type == 'income' %}📥{% else %}📤{% endif %} {{ t.type }}</td>
      <td>{{ t.account_name }}</td>
      <td><b style="color:{% if t.type == 'income' %}#27ae60{% else %}#e74c3c{% endif %}">
        {% if t.type == 'income' %}+{% else %}−{% endif %}{{ "%.2f"|format(t.amount) }} ₽
      </b></td>
      <td>{% if t.status == 'pending' %}⏳{% elif t.status == 'approved' %}✅{% else %}❌{% endif %} {{ t.status }}</td>
      <td style="font-size:12px">{{ t.seller_name or t.requester_name or '—' }}{% if t.order_id %}<br>Заказ #{{ t.order_id }}{% endif %}</td>
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
    f.write(T2)
print("OK finance_transactions.html")


# ============ 3. Детали транзакции ============
T3 = '''{% extends "base.html" %}{% block content %}
<h1>💳 Транзакция #{{ tx.id }}</h1>

<div class="card">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
    <div>
      <h3>Информация</h3>
      <p><b>Дата:</b> {{ tx.created_at }}</p>
      <p><b>Тип:</b> {% if tx.type == 'income' %}📥 Поступление{% else %}📤 Расход{% endif %}</p>
      <p><b>Счёт:</b> {{ tx.account_name }}</p>
      <p><b>Сумма:</b>
        <span style="font-size:22px;font-weight:900;color:{% if tx.type == 'income' %}#27ae60{% else %}#e74c3c{% endif %}">
          {% if tx.type == 'income' %}+{% else %}−{% endif %}{{ "%.2f"|format(tx.amount) }} ₽
        </span>
      </p>
      {% if tx.seller_name %}<p><b>Продавец:</b> {{ tx.seller_name }}</p>{% endif %}
      {% if tx.order_id %}<p><b>Заказ:</b> <a href="/orders/{{ tx.order_id }}">#{{ tx.order_id }}</a></p>{% endif %}
      {% if tx.comment %}<p><b>Комментарий:</b> {{ tx.comment }}</p>{% endif %}
    </div>
    <div>
      <h3>Статус</h3>
      <div style="font-size:24px;font-weight:900;color:{% if tx.status == 'pending' %}#f39c12{% elif tx.status == 'approved' %}#27ae60{% else %}#e74c3c{% endif %}">
        {% if tx.status == 'pending' %}⏳ Ожидает{% elif tx.status == 'approved' %}✅ Одобрено{% else %}❌ Отклонено{% endif %}
      </div>
      {% if tx.reviewed_at %}<p style="margin-top:12px;font-size:13px;color:#7f8c8d">Обработано: {{ tx.reviewed_at }}</p>{% endif %}
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
      <button name="approve" value="1" class="btn btn-success" type="submit">✅ Подтвердить</button>
      <button name="approve" value="0" class="btn btn-danger" type="submit">❌ Отклонить</button>
    </div>
  </form>
</div>
{% endif %}

<a href="/finance" class="btn">← Назад</a>
{% endblock %}'''

with open("templates/finance_transaction_detail.html", "w", encoding="utf-8") as f:
    f.write(T3)
print("OK finance_transaction_detail.html")


# ============ 4. Новая заявка на расход ============
T4 = '''{% extends "base.html" %}{% block content %}
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
      <button class="btn btn-danger" type="submit">📤 Отправить заявку</button>
      <a href="/finance" class="btn" style="background:#95a5a6">Отмена</a>
    </div>

    <p style="margin-top:12px;font-size:13px;color:#7f8c8d">
      Заявка будет ждать подтверждения. Деньги спишутся только после одобрения.
    </p>
  </form>
</div>
{% endblock %}'''

with open("templates/finance_new_expense.html", "w", encoding="utf-8") as f:
    f.write(T4)
print("OK finance_new_expense.html")

print()
print("=" * 50)
print("ALL TEMPLATES CREATED!")
print("=" * 50)
print()
print("Restart server.")