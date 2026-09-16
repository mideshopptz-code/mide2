# -*- coding: utf-8 -*-
import os

print("1. Adding DB methods...")

content = open("database.py", encoding="utf-8").read()

EXTRA = '''

    # ================= CUSTOMER PROFILE =================
    def get_customer_stats(self, customer_id):
        """Полная статистика покупателя"""
        with self.connect() as conn:
            r = conn.execute("""
                SELECT
                    COUNT(*) as total_orders,
                    SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) as delivered,
                    SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) as cancelled,
                    COALESCE(SUM(CASE WHEN status='delivered' THEN total_amount ELSE 0 END), 0) as total_spent
                FROM orders
                WHERE customer_id = ?
            """, (customer_id,)).fetchone()
            d = dict(r) if r else {}
            total_orders = d.get("delivered") or 0
            total_spent = d.get("total_spent") or 0
            d["avg_check"] = round(total_spent / total_orders, 2) if total_orders else 0
            return d

    def get_customer_orders(self, customer_id, limit=50):
        """Все заказы покупателя"""
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("""
                SELECT * FROM orders
                WHERE customer_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (customer_id, limit)).fetchall()]

    def get_customer_missions_progress(self, customer_id):
        """Все миссии с прогрессом покупателя"""
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("""
                SELECT m.*,
                       COALESCE(cmp.current_value, 0) as user_current,
                       COALESCE(cmp.status, 'not_started') as user_status,
                       cmp.claimed_at
                FROM missions m
                LEFT JOIN customer_mission_progress cmp
                  ON cmp.mission_id = m.id AND cmp.customer_id = ?
                WHERE m.is_active = 1
                ORDER BY m.id DESC
            """, (customer_id,)).fetchall()]
'''

if "def get_customer_stats" not in content:
    if not content.endswith("\n"):
        content += "\n"
    content += EXTRA
    open("database.py", "w", encoding="utf-8").write(content)
    print("   OK methods added")
else:
    print("   already exists")

print()
print("2. Adding route...")

web = open("web_app.py", encoding="utf-8").read()

NEW_ROUTES = '''

# ==================== CUSTOMER PROFILE ====================

@app.route("/customer/<int:cid>")
@login_required
def customer_profile(cid):
    """Просмотр профиля покупателя (для админа/сотрудников)"""
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
    """Мой профиль (для покупателя)"""
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

if "def customer_profile" not in web:
    marker = "# ================= WEBSOCKET ================="
    if marker in web:
        web = web.replace(marker, NEW_ROUTES + "\n\n" + marker)
        open("web_app.py", "w", encoding="utf-8").write(web)
        print("   OK routes added")
    else:
        print("   ERROR: marker not found")
else:
    print("   already exists")

print()
print("3. Creating templates...")

# ============================================================
# Шаблон профиля (для сотрудника)
# ============================================================
CUSTOMER_PROFILE = '''{% extends "base.html" %}{% block content %}

<h1>👤 {{ customer.name }}</h1>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:24px">
  <div class="card">
    <h3>📋 Личные данные</h3>
    <p><b>Имя:</b> {{ customer.name }}</p>
    <p><b>Телефон:</b> {{ customer.phone }}</p>
    {% if customer.district %}<p><b>Район:</b> {{ customer.district }}</p>{% endif %}
    <p><b>Регистрация:</b> {{ customer.created_at }}</p>
  </div>

  <div class="card">
    <h3>💰 Статистика</h3>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px">
      <div>
        <div style="font-size:12px;color:#7f8c8d">Заказов</div>
        <div style="font-size:28px;font-weight:900">{{ stats.delivered or 0 }}</div>
      </div>
      <div>
        <div style="font-size:12px;color:#7f8c8d">Потрачено</div>
        <div style="font-size:28px;font-weight:900">{{ "%.0f"|format(stats.total_spent or 0) }} ₽</div>
      </div>
      <div>
        <div style="font-size:12px;color:#7f8c8d">Средний чек</div>
        <div style="font-size:20px;font-weight:700">{{ "%.0f"|format(stats.avg_check or 0) }} ₽</div>
      </div>
      <div>
        <div style="font-size:12px;color:#7f8c8d">Бонусов</div>
        <div style="font-size:20px;font-weight:700;color:#f39c12">{{ customer.bonus_points or 0 }}</div>
      </div>
    </div>
  </div>
</div>

<div class="card">
  <h3>📦 Заказы ({{ orders|length }})</h3>
  {% if orders %}
  <table>
    <thead><tr>
      <th>ID</th><th>Дата</th><th>Сумма</th><th>Статус</th><th></th>
    </tr></thead>
    <tbody>
    {% for o in orders %}
    <tr>
      <td>#{{ o.id }}</td>
      <td style="font-size:12px">{{ o.created_at }}</td>
      <td><b>{{ "%.2f"|format(o.total_amount) }} ₽</b></td>
      <td>
        {% if o.status == 'new' %}🆕 Новый
        {% elif o.status == 'taken' %}📦 Принят
        {% elif o.status == 'delivered' %}✅ Доставлен
        {% elif o.status == 'cancelled' %}❌ Отменён
        {% else %}{{ o.status }}{% endif %}
      </td>
      <td><a href="/orders/{{ o.id }}" class="btn btn-sm">Открыть</a></td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p style="text-align:center;color:#7f8c8d;padding:20px">Заказов пока нет</p>
  {% endif %}
</div>

<div class="card">
  <h3>🎯 Миссии</h3>
  {% if missions %}
  <table>
    <thead><tr>
      <th>Миссия</th><th>Прогресс</th><th>Статус</th><th>Дата</th>
    </tr></thead>
    <tbody>
    {% for m in missions %}
    <tr>
      <td><b>{{ m.icon }} {{ m.title }}</b></td>
      <td>{{ m.user_current|int }} / {{ m.target_value|int }}</td>
      <td>
        {% if m.user_status == 'completed' %}✅ Выполнено
        {% elif m.user_status == 'pending_approval' %}⏳ На проверке
        {% elif m.user_status == 'rejected' %}❌ Отклонено
        {% elif m.user_status == 'in_progress' %}🔄 В процессе
        {% else %}⏸ Не начато{% endif %}
      </td>
      <td style="font-size:12px">{{ m.claimed_at or '-' }}</td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p style="text-align:center;color:#7f8c8d;padding:20px">Миссий нет</p>
  {% endif %}
</div>

<div style="margin-top:20px">
  <a href="javascript:history.back()" class="btn" style="background:#95a5a6">← Назад</a>
</div>

{% endblock %}'''

with open("templates/customer_profile.html", "w", encoding="utf-8") as f:
    f.write(CUSTOMER_PROFILE)
print("   OK templates/customer_profile.html")

# ============================================================
# Шаблон профиля для покупателя (со своим меню)
# ============================================================
MY_PROFILE = '''{% extends "shop/base.html" %}{% block content %}

<div class="hero" style="padding:60px 40px">
  <h2>{{ customer.name }}</h2>
  <p>{{ customer.phone }}</p>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:24px">
  <div class="card">
    <h3>💰 Мои баллы</h3>
    <div style="font-size:48px;font-weight:900;color:#ed1d36;margin:12px 0">
      {{ customer.bonus_points or 0 }}
    </div>
    <p style="color:#6b7280">1 балл = 1 ₽ скидки</p>
    <a href="/shop/bonus" class="btn btn-red" style="margin-top:14px;width:100%">Как потратить?</a>
  </div>

  <div class="card">
    <h3>📊 Моя статистика</h3>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px">
      <div>
        <div style="font-size:12px;color:#6b7280">Заказов</div>
        <div style="font-size:28px;font-weight:900">{{ stats.delivered or 0 }}</div>
      </div>
      <div>
        <div style="font-size:12px;color:#6b7280">Потрачено</div>
        <div style="font-size:28px;font-weight:900">{{ "%.0f"|format(stats.total_spent or 0) }} ₽</div>
      </div>
    </div>
  </div>
</div>

<div class="card">
  <h3>📦 Мои заказы ({{ orders|length }})</h3>
  {% if orders %}
  <table>
    <thead><tr>
      <th>ID</th><th>Дата</th><th>Сумма</th><th>Статус</th><th></th>
    </tr></thead>
    <tbody>
    {% for o in orders %}
    <tr>
      <td>#{{ o.id }}</td>
      <td style="font-size:12px">{{ o.created_at }}</td>
      <td><b>{{ "%.2f"|format(o.total_amount) }} ₽</b></td>
      <td>
        {% if o.status == 'new' %}🆕
        {% elif o.status == 'taken' %}📦
        {% elif o.status == 'delivered' %}✅
        {% else %}❌{% endif %}
        {{ o.status }}
      </td>
      <td><a href="/shop/orders/{{ o.id }}" class="btn btn-sm btn-red">Открыть</a></td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p style="text-align:center;color:#6b7280;padding:20px">Заказов пока нет</p>
  {% endif %}
</div>

<div class="card">
  <h3>🎯 Мои миссии</h3>
  <a href="/shop/missions" class="btn btn-red" style="margin-bottom:16px">Смотреть все миссии</a>
  {% if missions %}
  <table>
    <thead><tr>
      <th>Миссия</th><th>Прогресс</th><th>Статус</th>
    </tr></thead>
    <tbody>
    {% for m in missions if m.user_status != 'not_started' %}
    <tr>
      <td>{{ m.icon }} {{ m.title }}</td>
      <td>{{ m.user_current|int }} / {{ m.target_value|int }}</td>
      <td>
        {% if m.user_status == 'completed' %}✅ Выполнено
        {% elif m.user_status == 'pending_approval' %}⏳ На проверке
        {% elif m.user_status == 'rejected' %}❌ Отклонено
        {% else %}🔄 В процессе{% endif %}
      </td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p style="text-align:center;color:#6b7280;padding:20px">Активных миссий нет</p>
  {% endif %}
</div>

{% endblock %}'''

with open("templates/shop/my_profile.html", "w", encoding="utf-8") as f:
    f.write(MY_PROFILE)
print("   OK templates/shop/my_profile.html")

print()
print("Done!")