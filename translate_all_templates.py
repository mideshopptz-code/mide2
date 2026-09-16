# -*- coding: utf-8 -*-
import os
import re

print("=" * 60)
print("ПОЛНЫЙ ПЕРЕВОД ВСЕХ ШАБЛОНОВ")
print("=" * 60)
print()

# Словарь переводов — что на что заменить
REPLACEMENTS = [
    # ========== ЗАГОЛОВКИ h1 ==========
    ("<h1>Sales</h1>", "<h1>💰 Продажи</h1>"),
    ("<h1>My Products</h1>", "<h1>📦 Мои товары</h1>"),
    ("<h1>Customer Orders</h1>", "<h1>📋 Заказы покупателей</h1>"),
    ("<h1>Defect requests</h1>", "<h1>🚨 Заявки на брак</h1>"),
    ("<h1>Transfers</h1>", "<h1>🔄 Переводы</h1>"),
    ("<h1>My Team</h1>", "<h1>👥 Моя команда</h1>"),
    ("<h1>Revisions</h1>", "<h1>📝 Ревизии</h1>"),
    ("<h1>Employees</h1>", "<h1>👤 Сотрудники</h1>"),
    ("<h1>Dashboard</h1>", "<h1>📊 Панель управления</h1>"),
    ("<h1>KPI Leaderboard</h1>", "<h1>🏆 KPI рейтинг</h1>"),
    ("<h1>Delivery zones</h1>", "<h1>🗺️ Зоны доставки</h1>"),
    ("<h1>My Profile</h1>", "<h1>👤 Мой профиль</h1>"),
    ("<h1>Notifications</h1>", "<h1>🔔 Уведомления</h1>"),
    ("<h1>New sale</h1>", "<h1>💰 Новая продажа</h1>"),
    ("<h1>Add product</h1>", "<h1>➕ Добавить товар</h1>"),
    ("<h1>Edit product</h1>", "<h1>✏️ Редактировать товар</h1>"),
    ("<h1>Add employee</h1>", "<h1>➕ Добавить сотрудника</h1>"),
    ("<h1>Edit employee</h1>", "<h1>✏️ Редактировать сотрудника</h1>"),
    ("<h1>New transfer</h1>", "<h1>🔄 Новый перевод</h1>"),
    ("<h1>Request revision</h1>", "<h1>📝 Запросить ревизию</h1>"),
    ("<h1>New defect request</h1>", "<h1>🚨 Заявка на брак</h1>"),
    ("<h1>Add zone</h1>", "<h1>➕ Добавить зону</h1>"),
    ("<h1>New order</h1>", "<h1>📋 Новый заказ</h1>"),
    ("<h1>Profile</h1>", "<h1>👤 Профиль</h1>"),

    # ========== КНОПКИ ==========
    (">+ New sale<", ">+ Новая продажа<"),
    (">+ Add product<", ">+ Добавить товар<"),
    (">+ Add employee<", ">+ Добавить сотрудника<"),
    (">+ New defect<", ">+ Новый брак<"),
    (">+ New transfer<", ">+ Новый перевод<"),
    (">+ Request revision<", ">+ Запросить ревизию<"),
    (">+ Add zone<", ">+ Добавить зону<"),
    (">Edit<", ">Изменить<"),
    (">Del<", ">Удалить<"),
    (">Delete<", ">Удалить<"),
    (">Save<", ">Сохранить<"),
    (">Cancel<", ">Отмена<"),
    (">Open<", ">Открыть<"),
    (">View<", ">Просмотр<"),
    (">Send<", ">Отправить<"),
    (">Back<", ">Назад<"),
    (">Close<", ">Закрыть<"),
    (">Add<", ">Добавить<"),
    (">✓<", ">✓<"),
    (">✗<", ">✗<"),

    # ========== ЗАГОЛОВКИ ТАБЛИЦ ==========
    ("<th>ID</th>", "<th>№</th>"),
    ("<th>NAME</th>", "<th>НАЗВАНИЕ</th>"),
    ("<th>CATEGORY</th>", "<th>КАТЕГОРИЯ</th>"),
    ("<th>QTY</th>", "<th>КОЛ-ВО</th>"),
    ("<th>PRICE</th>", "<th>ЦЕНА</th>"),
    ("<th>SELLER</th>", "<th>ПРОДАВЕЦ</th>"),
    ("<th>PRODUCT</th>", "<th>ТОВАР</th>"),
    ("<th>EXPECTED</th>", "<th>ОЖИДАЕТСЯ</th>"),
    ("<th>ACTUAL</th>", "<th>ФАКТ</th>"),
    ("<th>STATUS</th>", "<th>СТАТУС</th>"),
    ("<th>CUSTOMER</th>", "<th>КЛИЕНТ</th>"),
    ("<th>PHONE</th>", "<th>ТЕЛЕФОН</th>"),
    ("<th>ADDRESS</th>", "<th>АДРЕС</th>"),
    ("<th>TOTAL</th>", "<th>ИТОГО</th>"),
    ("<th>STAFF</th>", "<th>СОТРУДНИК</th>"),
    ("<th>FROM</th>", "<th>ОТ КОГО</th>"),
    ("<th>TO</th>", "<th>КОМУ</th>"),
    ("<th>ADMIN?</th>", "<th>АДМИН?</th>"),
    ("<th>ROLE</th>", "<th>ДОЛЖНОСТЬ</th>"),
    ("<th>PRODUCTS</th>", "<th>ТОВАРОВ</th>"),
    ("<th>STOCK VALUE</th>", "<th>СТОИМОСТЬ</th>"),
    ("<th>REQUESTER</th>", "<th>ЗАПРОСИЛ</th>"),
    ("<th>TARGET</th>", "<th>ЦЕЛЬ</th>"),
    ("<th>CREATED</th>", "<th>СОЗДАНО</th>"),
    ("<th>USERNAME</th>", "<th>ЛОГИН</th>"),
    ("<th>FULL NAME</th>", "<th>ПОЛНОЕ ИМЯ</th>"),
    ("<th>ACTIONS</th>", "<th>ДЕЙСТВИЯ</th>"),
    ("<th>REASON</th>", "<th>ПРИЧИНА</th>"),
    ("<th>REVENUE</th>", "<th>ВЫРУЧКА</th>"),
    ("<th>ORDERS</th>", "<th>ЗАКАЗОВ</th>"),
    ("<th>SALES</th>", "<th>ПРОДАЖ</th>"),
    ("<th>ACCURACY</th>", "<th>ТОЧНОСТЬ</th>"),
    ("<th>#</th>", "<th>#</th>"),
    ("<th>FEE</th>", "<th>СТОИМОСТЬ</th>"),
    ("<th>FREE FROM</th>", "<th>БЕСПЛАТНО ОТ</th>"),
    ("<th>ETA</th>", "<th>ВРЕМЯ</th>"),

    # ========== СТАТИСТИКА ==========
    ("<h3>Products</h3>", "<h3>Товаров</h3>"),
    ("<h3>Total value</h3>", "<h3>Общая стоимость</h3>"),
    ("<h3>Low stock</h3>", "<h3>Мало на складе</h3>"),
    ("<h3>Top products</h3>", "<h3>🏆 Топ товаров</h3>"),
    ("<h3>Top sellers</h3>", "<h3>🏆 Топ продавцов</h3>"),
    ("<h3>Add zone</h3>", "<h3>➕ Добавить зону</h3>"),
    ("<h3>Items</h3>", "<h3>🛒 Состав заказа</h3>"),
    ("<h3>Comments</h3>", "<h3>💬 Комментарии</h3>"),
    ("<h3>Info</h3>", "<h3>📋 Информация</h3>"),
    ("<h3>Telegram notifications</h3>", "<h3>📱 Telegram-уведомления</h3>"),
    ("<h3>Edit name</h3>", "<h3>✏️ Изменить имя</h3>"),
    ("<h3>Actions</h3>", "<h3>Действия</h3>"),
    ("<h3>Status</h3>", "<h3>Статус</h3>"),
    ("<h3>Информация</h3>", "<h3>📋 Информация</h3>"),
    ("TOTAL ORDERS", "ВСЕГО ЗАКАЗОВ"),
    ("DELIVERED", "ДОСТАВЛЕНО"),
    ("REVENUE", "ВЫРУЧКА"),
    ("PRODUCTS", "ТОВАРОВ"),
    ("TOTAL VALUE", "ОБЩАЯ СТОИМОСТЬ"),
    ("LOW STOCK", "МАЛО НА СКЛАДЕ"),

    # ========== ФОРМЫ ==========
    ("<label>Name</label>", "<label>Название</label>"),
    ("<label>Category</label>", "<label>Категория</label>"),
    ("<label>Quantity</label>", "<label>Количество</label>"),
    ("<label>Price</label>", "<label>Цена</label>"),
    ("<label>Min stock</label>", "<label>Мин. остаток</label>"),
    ("<label>Username</label>", "<label>Логин</label>"),
    ("<label>Password", "<label>Пароль"),
    ("<label>Full name</label>", "<label>Полное имя</label>"),
    ("<label>Role</label>", "<label>Должность</label>"),
    ("<label>Manager (who this employee reports to)</label>", "<label>Руководитель</label>"),
    ("<label>Commission rate (%)</label>", "<label>Размер комиссии (%)</label>"),
    ("<label>Comment</label>", "<label>Комментарий</label>"),
    ("<label>Reason</label>", "<label>Причина</label>"),
    ("<label>To employee</label>", "<label>Кому передать</label>"),
    ("<label>Product</label>", "<label>Товар</label>"),
    ("<label>Who to check</label>", "<label>Кого проверить</label>"),
    ("<label>Add image</label>", "<label>Добавить фото</label>"),
    ("<label>Account *</label>", "<label>Счёт *</label>"),
    ("<label>Delivery address *</label>", "<label>Адрес доставки *</label>"),
    ("<label>Аmount (RUB) *</label>", "<label>Сумма (₽) *</label>"),
    ("<label>Amount (RUB) *</label>", "<label>Сумма (₽) *</label>"),
    ("<label>Комментарий (опционально)</label>", "<label>Комментарий (опционально)</label>"),
    ("<label>Delivery address *</label>", "<label>Адрес доставки *</label>"),
    ("<label>Full name</label>", "<label>Полное имя</label>"),
    ("<label>Email</label>", "<label>Email</label>"),

    # ========== МЕСТА ==========
    ("placeholder=\"Name\"", "placeholder=\"Название\""),
    ("placeholder=\"Category\"", "placeholder=\"Категория\""),
    ("placeholder=\"Fee\"", "placeholder=\"Стоимость\""),
    ("placeholder=\"Free from\"", "placeholder=\"Бесплатно от\""),
    ("placeholder=\"ETA min\"", "placeholder=\"Время доставки\""),
    ("placeholder=\"Message...\"", "placeholder=\"Написать сообщение...\""),
    ("placeholder=\"What happened?\"", "placeholder=\"Что случилось?\""),
    ("placeholder=\"Что сделали\"", "placeholder=\"Что сделали\""),

    # ========== ТЕКСТЫ ==========
    (">No sales<", ">Продаж нет<"),
    (">No products<", ">Товаров нет<"),
    (">No orders<", ">Заказов нет<"),
    (">No defects<", ">Дефектов нет<"),
    (">No data<", ">Нет данных<"),
    (">No zones<", ">Зон нет<"),
    (">No users<", ">Пользователей нет<"),
    (">No notifications<", ">Уведомлений нет<"),
    (">No transfers<", ">Переводов нет<"),
    (">No revisions<", ">Ревизий нет<"),
    (">No images<", ">Фото нет<"),
    (">No comments<", ">Комментариев нет<"),
    (">No comments yet<", ">Комментариев пока нет<"),
    (">No subordinate<", ">Подчинённых нет<"),
    ("No subordinates yet", "Пока нет подчинённых"),

    # ========== СТАТУСЫ ==========
    ("New", "Новый"),
    ("Taken", "Принят"),
    ("Delivered", "Доставлен"),
    ("Cancelled", "Отменён"),
    (">pending<", ">⏳ ожидает<"),
    (">approved<", ">✅ одобрено<"),
    (">rejected<", ">❌ отклонено<"),
    (">completed<", ">✅ завершён<"),

    # ========== ВАЛЮТЫ ==========
    (" RUB", " ₽"),
    ("руб.", "₽"),
    ("RUB</", "₽</"),
    ("RUB ", "₽ "),

    # ========== РОЛИ (бейджи) ==========
    (">Administrator<", ">Администратор<"),
    (">Seller<", ">Продавец<"),
    (">Mentor<", ">Наставник<"),
    (">Senior Seller<", ">Старший продавец<"),
    (">Accountant<", ">Бухгалтер<"),
]


# Обрабатываем ВСЕ файлы в templates/ и templates/shop/
def process_file(path):
    try:
        content = open(path, encoding="utf-8").read()
    except Exception as e:
        return False
    
    original = content
    
    for old, new in REPLACEMENTS:
        if old in content:
            content = content.replace(old, new)
    
    if content != original:
        open(path, "w", encoding="utf-8").write(content)
        return True
    return False


count = 0
total = 0

# В templates/
for fname in os.listdir("templates"):
    if fname.endswith(".html"):
        path = os.path.join("templates", fname)
        if process_file(path):
            count += 1
            print("  OK templates/" + fname)
        total += 1

# В templates/shop/
if os.path.exists("templates/shop"):
    for fname in os.listdir("templates/shop"):
        if fname.endswith(".html"):
            path = os.path.join("templates/shop", fname)
            if process_file(path):
                count += 1
                print("  OK templates/shop/" + fname)
            total += 1

print()
print("=" * 60)
print("ОБРАБОТАНО ФАЙЛОВ:", total)
print("ИЗМЕНЕНО:", count)
print("=" * 60)
print()
print("Restart server + Ctrl+F5 in browser.")