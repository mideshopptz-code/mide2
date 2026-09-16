# -*- coding: utf-8 -*-
import os

print("1. Updating admin_missions.html...")
content = open("templates/admin_missions.html", encoding="utf-8").read()

# Ссылка на профиль в pending
old = "<td>{{ p.customer_name }}<br><small>{{ p.customer_phone }}</small></td>"
new = '<td><a href="/customer/{{ p.customer_id }}" style="color:#3498db;text-decoration:none"><b>{{ p.customer_name }}</b></a><br><small>{{ p.customer_phone }}</small></td>'

if old in content:
    content = content.replace(old, new)
    print("   OK: pending customer link")
else:
    print("   WARN: pending link pattern not found")

# Колонка со статистикой
old_table = '<td>{% if m.is_active %}✅{% else %}🚫{% endif %}</td>'
new_table = '''<td>{% if m.is_active %}✅{% else %}🚫{% endif %}</td>
      <td style="font-size:13px">
        {% if stats and stats[m.id] %}
          <b>✅ {{ stats[m.id].done_count }}</b> выполнили
          {% if stats[m.id].pending_count %}<br>⏳ {{ stats[m.id].pending_count }} ждут{% endif %}
          {% if stats[m.id].progress_count %}<br>🔄 {{ stats[m.id].progress_count }} в процессе{% endif %}
        {% else %}—{% endif %}
      </td>'''

if old_table in content and "done_count" not in content:
    content = content.replace(old_table, new_table, 1)
    print("   OK: mission stats column added")
else:
    print("   WARN: stats column pattern not found or already exists")

# Заголовок колонки
old_headers = '<th>Активна</th><th>Действия</th>'
new_headers = '<th>Активна</th><th>Статистика</th><th>Действия</th>'
if old_headers in content and "Статистика" not in content:
    content = content.replace(old_headers, new_headers)
    print("   OK: header added")

open("templates/admin_missions.html", "w", encoding="utf-8").write(content)


print()
print("2. Updating shop/base.html...")
content = open("templates/shop/base.html", encoding="utf-8").read()

if '/shop/profile' not in content:
    old_nav = '<a href="/shop/logout" class="nav-link">Выйти</a>'
    new_nav = '<a href="/shop/profile" class="nav-link">Профиль</a>\n    <a href="/shop/logout" class="nav-link">Выйти</a>'
    if old_nav in content:
        content = content.replace(old_nav, new_nav)
        open("templates/shop/base.html", "w", encoding="utf-8").write(content)
        print("   OK: profile link added to shop nav")
    else:
        print("   WARN: nav pattern not found")
else:
    print("   already has profile link")


print()
print("3. Updating staff_order_detail.html...")
content = open("templates/staff_order_detail.html", encoding="utf-8").read()

old = '<p><b>Customer:</b> {{ order.customer_name }} - {{ order.customer_phone }}</p>'
new = '<p><b>Customer:</b> <a href="/customer/{{ order.customer_id }}" style="color:#3498db">{{ order.customer_name }}</a> - {{ order.customer_phone }}</p>'

if old in content and "/customer/" not in content:
    content = content.replace(old, new)
    open("templates/staff_order_detail.html", "w", encoding="utf-8").write(content)
    print("   OK: order detail customer link added")
else:
    print("   pattern not found or already added")


print()
print("4. Updating shop_orders.html (list)...")
content = open("templates/staff_orders.html", encoding="utf-8").read()

old = '<td>{{ o.customer_name }}</td>'
new = '<td><a href="/customer/{{ o.customer_id }}" style="color:#3498db">{{ o.customer_name }}</a></td>'

if old in content and "/customer/" not in content:
    content = content.replace(old, new, 1)
    open("templates/staff_orders.html", "w", encoding="utf-8").write(content)
    print("   OK: orders list customer link added")
else:
    print("   pattern not found or already added")


print()
print("Done! Restart server.")