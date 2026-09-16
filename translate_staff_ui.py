# -*- coding: utf-8 -*-
import re
import os

print("Translating staff UI to Russian...")
print()

# ============================================================
# 1. BASE.HTML — главное меню
# ============================================================
print("1. Updating base.html (menu)...")

content = open("templates/base.html", encoding="utf-8").read()

# Полностью новый nav
nav_match = re.search(r'<nav>.*?</nav>', content, re.DOTALL)
if nav_match:
    NEW_NAV = '''<nav>
  <strong>Склад</strong>
  {% if user %}
    {% if user.role == 'accountant' %}
      <a href="/finance">💰 Финансы</a>
      <a href="/finance/transactions?type=income">📥 Поступления</a>
      <a href="/finance/transactions?type=expense">📤 Заявки</a>
      <a href="/admin/bank-accounts">💳 Счета</a>
      <a href="/notifications">🔔 Уведомления</a>
    {% else %}
      <a href="/">📦 Товары</a>
      <a href="/sales">💰 Продажи</a>
      <a href="/orders">📋 Заказы</a>
      <a href="/defects">🚨 Дефекты</a>
      <a href="/transfers">🔄 Переводы</a>
      {% if user.role in ('admin','senior_seller','mentor') %}
        <a href="/team">👥 Команда</a>
        <a href="/revisions">📝 Ревизии</a>
      {% endif %}
      {% if user.role == 'admin' %}
        <a href="/staff">👤 Сотрудники</a>
        <a href="/missions">🎯 Миссии</a>
      {% endif %}
      <a href="/dashboard">📊 Панель управления</a>
      {% if user.role in ('admin','senior_seller','mentor') %}
        <a href="/kpi">🏆 KPI</a>
      {% endif %}
      {% if user.role == 'admin' %}
        <a href="/zones">🗺️ Зоны</a>
      {% endif %}
      {% if user.role in ('admin', 'accountant') %}
        <a href="/finance">💰 Финансы</a>
      {% endif %}
      <a href="/profile">👤 Профиль</a>
      <a href="/notifications">🔔 Уведомления</a>
    {% endif %}
    <span style="margin-left:auto;font-size:13px">
      {{ user.full_name or user.username }}
      <span class="role-badge role-{{ user.role }}">{{ user.role }}</span>
    </span>
    <a href="/logout">Выход</a>
  {% endif %}
</nav>'''
    content = content.replace(nav_match.group(0), NEW_NAV)
    open("templates/base.html", "w", encoding="utf-8").write(content)
    print("   OK: menu translated")


# ============================================================
# 2. Переводим шаблоны
# ============================================================
print()
print("2. Translating templates...")

# Словарь: что заменить на что
TRANSLATIONS = [
    # Кнопки
    ('>Save<', '>Сохранить<'),
    ('>Cancel<', '>Отмена<'),
    ('>Delete<', '>Удалить<'),
    ('>Edit<', '>Изменить<'),
    ('>Del<', '>Удалить<'),
    ('>Open<', '>Открыть<'),
    ('>Close<', '>Закрыть<'),
    ('>Add<', '>Добавить<'),
    ('>Back<', '>Назад<'),
    ('>Send<', '>Отправить<'),

    # Заголовки
    ('<h1>My Products</h1>', '<h1>📦 Мои товары</h1>'),
    ('<h1>Products</h1>', '<h1>📦 Товары</h1>'),
    ('<h1>Sales</h1>', '<h1>💰 Продажи</h1>'),
    ('<h1>Customer Orders</h1>', '<h1>📋 Заказы покупателей</h1>'),
    ('<h1>Defect requests</h1>', '<h1>🚨 Заявки на брак</h1>'),
    ('<h1>Defects</h1>', '<h1>🚨 Дефекты</h1>'),
    ('<h1>Transfers</h1>', '<h1>🔄 Переводы</h1>'),
    ('<h1>Revisions</h1>', '<h1>📝 Ревизии</h1>'),
    ('<h1>My Team</h1>', '<h1>👥 Моя команда</h1>'),
    ('<h1>Employees</h1>', '<h1>👤 Сотрудники</h1>'),
    ('<h1>Notifications</h1>', '<h1>🔔 Уведомления</h1>'),
    ('<h1>Dashboard</h1>', '<h1>📊 Панель управления</h1>'),
    ('<h1>KPI Leaderboard</h1>', '<h1>🏆 KPI рейтинг</h1>'),
    ('<h1>Delivery zones</h1>', '<h1>🗺️ Зоны доставки</h1>'),
    ('<h1>My Profile</h1>', '<h1>👤 Мой профиль</h1>'),

    # Поля форм
    ('<label>Name</label>', '<label>Название</label>'),
    ('<label>Category</label>', '<label>Категория</label>'),
    ('<label>Quantity</label>', '<label>Количество</label>'),
    ('<label>Price</label>', '<label>Цена</label>'),
    ('<label>Min stock</label>', '<label>Мин. остаток</label>'),
    ('<label>Username</label>', '<label>Логин</label>'),
    ('<label>Password', '<label>Пароль'),
    ('<label>Full name</label>', '<label>Полное имя</label>'),
    ('<label>Role</label>', '<label>Должность</label>'),
    ('<label>Manager (who this employee reports to)</label>',
     '<label>Руководитель</label>'),
    ('<label>Commission rate (%)</label>', '<label>Размер комиссии (%)</label>'),
    ('<label>Comment</label>', '<label>Комментарий</label>'),
    ('<label>Reason</label>', '<label>Причина</label>'),
    ('<label>To employee</label>', '<label>Кому передать</label>'),
    ('<label>Product</label>', '<label>Товар</label>'),
    ('<label>Who to check</label>', '<label>Кого проверить</label>'),
    ('<label>Add image</label>', '<label>Добавить фото</label>'),
    ('<label>Amount (RUB) *</label>', '<label>Сумма (₽) *</label>'),

    # Placeholder
    ('placeholder="Name"', 'placeholder="Название"'),
    ('placeholder="Category"', 'placeholder="Категория"'),
    ('placeholder="Fee"', 'placeholder="Стоимость"'),
    ('placeholder="Free from"', 'placeholder="Бесплатно от"'),
    ('placeholder="ETA min"', 'placeholder="Мин. доставки"'),

    # Заголовки таблиц
    ('<th>ID</th>', '<th>№</th>'),
    ('<th>Name</th>', '<th>Название</th>'),
    ('<th>Category</th>', '<th>Категория</th>'),
    ('<th>Qty</th>', '<th>Кол-во</th>'),
    ('<th>Quantity</th>', '<th>Количество</th>'),
    ('<th>Price</th>', '<th>Цена</th>'),
    ('<th>Revenue</th>', '<th>Выручка</th>'),
    ('<th>Seller</th>', '<th>Продавец</th>'),
    ('<th>Status</th>', '<th>Статус</th>'),
    ('<th>Total</th>', '<th>Итого</th>'),
    ('<th>Customer</th>', '<th>Клиент</th>'),
    ('<th>Phone</th>', '<th>Телефон</th>'),
    ('<th>Address</th>', '<th>Адрес</th>'),
    ('<th>Staff</th>', '<th>Сотрудник</th>'),
    ('<th>Actions</th>', '<th>Действия</th>'),
    ('<th>Role</th>', '<th>Должность</th>'),
    ('<th>Created</th>', '<th>Создан</th>'),

    # Статусы
    ('New', 'Новый'),
    ('Taken', 'Принят'),
    ('Delivered', 'Доставлен'),
    ('Cancelled', 'Отменён'),
    ('pending', '⏳ ожидает'),
    ('approved', '✅ одобрено'),
    ('rejected', '❌ отклонено'),

    # Разное
    ('<h3>Top products</h3>', '<h3>🏆 Топ товаров</h3>'),
    ('<h3>Top sellers</h3>', '<h3>🏆 Топ продавцов</h3>'),
    ('<h3>Add zone</h3>', '<h3>➕ Добавить зону</h3>'),
    ('<h3>Заказы', '<h3>📦 Заказы'),
    ('No products', 'Нет товаров'),
    ('No orders', 'Нет заказов'),
    ('No sales', 'Нет продаж'),
    ('No data', 'Нет данных'),
    ('No users', 'Нет пользователей'),
    ('No zones', 'Нет зон'),
    ('No notifications', 'Нет уведомлений'),
    ('No defects', 'Нет дефектов'),
    ('No transfers', 'Нет переводов'),
    ('No revisions', 'Нет ревизий'),
    ('No images', 'Нет фото'),
    ('No subordinates yet', 'Пока нет подчинённых'),
]


# Обрабатываем все файлы в templates/
files_to_translate = [
    "templates/index.html",
    "templates/product_form.html",
    "templates/staff.html",
    "templates/staff_form.html",
    "templates/staff_orders.html",
    "templates/staff_order_detail.html",
    "templates/sales.html",
    "templates/sale_new.html",
    "templates/defects.html",
    "templates/defect_new.html",
    "templates/transfers.html",
    "templates/transfer_new.html",
    "templates/revisions.html",
    "templates/revision_new.html",
    "templates/revision_detail.html",
    "templates/team.html",
    "templates/team_member.html",
    "templates/notifications.html",
    "templates/dashboard.html",
    "templates/kpi.html",
    "templates/zones.html",
    "templates/product_images.html",
    "templates/profile.html",
    "templates/login.html",
    "templates/register.html",
]

count_files = 0
count_repl = 0

for fname in files_to_translate:
    if not os.path.exists(fname):
        continue
    content = open(fname, encoding="utf-8").read()
    original = content
    
    for old, new in TRANSLATIONS:
        if old in content:
            content = content.replace(old, new)
            count_repl += 1
    
    if content != original:
        open(fname, "w", encoding="utf-8").write(content)
        count_files += 1
        print("   OK " + fname)

print()
print("Translated files:", count_files)
print("Total replacements:", count_repl)

# ============================================================
# 3. Роль бухгалтера в staff_form
# ============================================================
print()
print("3. Ensuring accountant role in staff_form...")

content = open("templates/staff_form.html", encoding="utf-8").read()

if 'value="accountant"' not in content:
    # Ищем seller option
    m = re.search(r'(<option value="seller"[^>]*>[^<]*</option>)', content)
    if m:
        seller_line = m.group(1)
        accountant_line = '\n        <option value="accountant" {% if user and user.role == \'accountant\' %}selected{% endif %}>💼 Бухгалтер</option>'
        content = content.replace(seller_line, seller_line + accountant_line)
        open("templates/staff_form.html", "w", encoding="utf-8").write(content)
        print("   OK: accountant option added")

# Также переводим селект ролей
content = open("templates/staff_form.html", encoding="utf-8").read()
content = content.replace(">Senior Seller<", ">🌟 Старший продавец<")
content = content.replace(">Mentor<", ">📚 Наставник<")
content = content.replace(">Seller<", ">👤 Продавец<")
content = content.replace(">Administrator<", ">👑 Администратор<")
open("templates/staff_form.html", "w", encoding="utf-8").write(content)
print("   OK: roles translated")

# ============================================================
# 4. Роль в веб_апп для отображения
# ============================================================
print()
print("4. Updating role labels...")

web = open("web_app.py", encoding="utf-8").read()
if 'ROLE_LABELS = {' in web:
    web = re.sub(
        r'ROLE_LABELS = \{[^}]+\}',
        '''ROLE_LABELS = {
    "admin": "👑 Администратор",
    "senior_seller": "🌟 Старший продавец",
    "mentor": "📚 Наставник",
    "seller": "👤 Продавец",
    "accountant": "💼 Бухгалтер",
}''',
        web
    )
    open("web_app.py", "w", encoding="utf-8").write(web)
    print("   OK: ROLE_LABELS updated")

# ============================================================
# 5. Проверка синтаксиса
# ============================================================
print()
print("5. Syntax check...")
import ast
try:
    ast.parse(open("web_app.py", encoding="utf-8").read())
    print("   web_app.py OK")
except SyntaxError as e:
    print("   ERROR:", e.lineno, e.msg)

print()
print("=" * 50)
print("DONE!")
print("=" * 50)
print()
print("Restart server + Ctrl+F5 in browser.")