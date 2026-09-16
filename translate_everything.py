# -*- coding: utf-8 -*-
import os
import re

print("=" * 70)
print("ПОЛНЫЙ ПЕРЕВОД ВСЕГО НА РУССКИЙ")
print("=" * 70)
print()

# ============================================================
# СЛОВАРЬ ПЕРЕВОДОВ
# ============================================================
REPLACEMENTS = [
    # ========== ЗАГОЛОВКИ h1/h2/h3 ==========
    (">Sales<", ">💰 Продажи<"),
    (">My Products<", ">📦 Мои товары<"),
    (">Customer Orders<", ">📋 Заказы покупателей<"),
    (">Defect requests<", ">🚨 Заявки на брак<"),
    (">Defects<", ">🚨 Брак<"),
    (">Transfers<", ">🔄 Переводы<"),
    (">My Team<", ">👥 Моя команда<"),
    (">Revisions<", ">📝 Ревизии<"),
    (">Employees<", ">👤 Сотрудники<"),
    (">Dashboard<", ">📊 Панель управления<"),
    (">KPI Leaderboard<", ">🏆 KPI рейтинг<"),
    (">Delivery zones<", ">🗺️ Зоны доставки<"),
    (">My Profile<", ">👤 Мой профиль<"),
    (">Notifications<", ">🔔 Уведомления<"),
    (">New sale<", ">💰 Новая продажа<"),
    (">Add product<", ">➕ Добавить товар<"),
    (">Edit product<", ">✏️ Редактировать товар<"),
    (">Add employee<", ">➕ Добавить сотрудника<"),
    (">Edit employee<", ">✏️ Редактировать сотрудника<"),
    (">New transfer<", ">🔄 Новый перевод<"),
    (">Request revision<", ">📝 Запросить ревизию<"),
    (">New defect<", ">🚨 Новый брак<"),
    (">Add zone<", ">➕ Добавить зону<"),
    (">Profile<", ">👤 Профиль<"),
    (">Login<", ">🔐 Вход<"),
    (">Register<", ">📝 Регистрация<"),
    (">Top products<", ">🏆 Топ товаров<"),
    (">Top sellers<", ">🏆 Топ продавцов<"),
    (">Items<", ">🛒 Состав заказа<"),
    (">Comments<", ">💬 Комментарии<"),
    (">Info<", ">📋 Информация<"),
    (">Telegram notifications<", ">📱 Telegram-уведомления<"),
    (">Edit name<", ">✏️ Изменить имя<"),
    (">Actions<", ">⚙️ Действия<"),
    (">Status<", ">📊 Статус<"),
    (">Информация<", ">📋 Информация<"),
    (">Missions<", ">🎯 Миссии<"),
    (">Магазин<", ">🛍️ Магазин<"),
    (">Каталог товаров<", ">🛍️ Каталог товаров<"),
    (">Мои заказы<", ">📋 Мои заказы<"),
    (">Корзина<", ">🛒 Корзина<"),
    (">Вход<", ">🔐 Вход<"),
    (">Регистрация<", ">📝 Регистрация<"),
    (">Профиль<", ">👤 Профиль<"),
    (">Мои бонусы<", ">🎁 Мои бонусы<"),

    # ========== КНОПКИ ==========
    (">New sale<", ">+ Новая продажа<"),
    (">Add product<", ">+ Добавить товар<"),
    (">Add employee<", ">+ Добавить сотрудника<"),
    (">New defect<", ">+ Новый брак<"),
    (">New transfer<", ">+ Новый перевод<"),
    (">Request revision<", ">+ Запросить ревизию<"),
    (">Add zone<", ">+ Добавить зону<"),
    (">Edit<", ">✏️ Изменить<"),
    (">Delete<", ">🗑️ Удалить<"),
    (">Del<", ">🗑️ Удалить<"),
    (">Save<", ">💾 Сохранить<"),
    (">Cancel<", ">Отмена<"),
    (">Open<", ">Открыть<"),
    (">View<", ">Просмотр<"),
    (">Send<", ">📤 Отправить<"),
    (">Back<", ">← Назад<"),
    (">Close<", ">Закрыть<"),
    (">Add<", ">Добавить<"),
    (">Request<", ">Отправить<"),
    (">Create transfer<", ">Создать перевод<"),
    (">Send request<", ">Отправить заявку<"),
    (">Send for approval<", ">Отправить на подтверждение<"),
    (">Unlink<", ">Отвязать<"),
    (">Claim reward<", ">🎁 Забрать награду<"),
    (">Добавить в корзину<", ">🛒 В корзину<"),
    (">Place order<", ">✅ Оформить заказ<"),
    (">Login<", ">🔐 Войти<"),
    (">Register<", ">📝 Зарегистрироваться<"),
    (">Logout<", ">Выход<"),
    (">Выход<", ">Выход<"),

    # ========== ЗАГОЛОВКИ ТАБЛИЦ ==========
    ("<th>ID</th>", "<th>№</th>"),
    ("<th>№</th>", "<th>№</th>"),
    ("<th>NAME</th>", "<th>НАЗВАНИЕ</th>"),
    ("<th>Name</th>", "<th>Название</th>"),
    ("<th>CATEGORY</th>", "<th>КАТЕГОРИЯ</th>"),
    ("<th>Category</th>", "<th>Категория</th>"),
    ("<th>QTY</th>", "<th>КОЛ-ВО</th>"),
    ("<th>Qty</th>", "<th>Кол-во</th>"),
    ("<th>Quantity</th>", "<th>Количество</th>"),
    ("<th>PRICE</th>", "<th>ЦЕНА</th>"),
    ("<th>Price</th>", "<th>Цена</th>"),
    ("<th>SELLER</th>", "<th>ПРОДАВЕЦ</th>"),
    ("<th>Seller</th>", "<th>Продавец</th>"),
    ("<th>PRODUCT</th>", "<th>ТОВАР</th>"),
    ("<th>Product</th>", "<th>Товар</th>"),
    ("<th>EXPECTED</th>", "<th>ОЖИДАЕТСЯ</th>"),
    ("<th>ACTUAL</th>", "<th>ФАКТ</th>"),
    ("<th>STATUS</th>", "<th>СТАТУС</th>"),
    ("<th>Status</th>", "<th>Статус</th>"),
    ("<th>CUSTOMER</th>", "<th>КЛИЕНТ</th>"),
    ("<th>Customer</th>", "<th>Клиент</th>"),
    ("<th>PHONE</th>", "<th>ТЕЛЕФОН</th>"),
    ("<th>Phone</th>", "<th>Телефон</th>"),
    ("<th>ADDRESS</th>", "<th>АДРЕС</th>"),
    ("<th>Address</th>", "<th>Адрес</th>"),
    ("<th>TOTAL</th>", "<th>ИТОГО</th>"),
    ("<th>Total</th>", "<th>Итого</th>"),
    ("<th>STAFF</th>", "<th>СОТРУДНИК</th>"),
    ("<th>Staff</th>", "<th>Сотрудник</th>"),
    ("<th>FROM</th>", "<th>ОТ КОГО</th>"),
    ("<th>From</th>", "<th>От кого</th>"),
    ("<th>TO</th>", "<th>КОМУ</th>"),
    ("<th>To</th>", "<th>Кому</th>"),
    ("<th>ADMIN?</th>", "<th>АДМИН?</th>"),
    ("<th>ROLE</th>", "<th>ДОЛЖНОСТЬ</th>"),
    ("<th>Role</th>", "<th>Должность</th>"),
    ("<th>PRODUCTS</th>", "<th>ТОВАРОВ</th>"),
    ("<th>Products</th>", "<th>Товаров</th>"),
    ("<th>STOCK VALUE</th>", "<th>СТОИМОСТЬ</th>"),
    ("<th>REQUESTER</th>", "<th>ЗАПРОСИЛ</th>"),
    ("<th>Requester</th>", "<th>Запросил</th>"),
    ("<th>TARGET</th>", "<th>ЦЕЛЬ</th>"),
    ("<th>Target</th>", "<th>Цель</th>"),
    ("<th>CREATED</th>", "<th>СОЗДАНО</th>"),
    ("<th>Created</th>", "<th>Создано</th>"),
    ("<th>USERNAME</th>", "<th>ЛОГИН</th>"),
    ("<th>Username</th>", "<th>Логин</th>"),
    ("<th>FULL NAME</th>", "<th>ПОЛНОЕ ИМЯ</th>"),
    ("<th>Full name</th>", "<th>Полное имя</th>"),
    ("<th>ACTIONS</th>", "<th>ДЕЙСТВИЯ</th>"),
    ("<th>Actions</th>", "<th>Действия</th>"),
    ("<th>REASON</th>", "<th>ПРИЧИНА</th>"),
    ("<th>Reason</th>", "<th>Причина</th>"),
    ("<th>REVENUE</th>", "<th>ВЫРУЧКА</th>"),
    ("<th>Revenue</th>", "<th>Выручка</th>"),
    ("<th>ORDERS</th>", "<th>ЗАКАЗОВ</th>"),
    ("<th>Orders</th>", "<th>Заказов</th>"),
    ("<th>SALES</th>", "<th>ПРОДАЖ</th>"),
    ("<th>Sales</th>", "<th>Продаж</th>"),
    ("<th>ACCURACY</th>", "<th>ТОЧНОСТЬ</th>"),
    ("<th>Accuracy</th>", "<th>Точность</th>"),
    ("<th>FEE</th>", "<th>СТОИМОСТЬ</th>"),
    ("<th>Fee</th>", "<th>Стоимость</th>"),
    ("<th>FREE FROM</th>", "<th>БЕСПЛАТНО ОТ</th>"),
    ("<th>Free from</th>", "<th>Бесплатно от</th>"),
    ("<th>ETA</th>", "<th>ВРЕМЯ</th>"),
    ("<th>Order ID</th>", "<th>№ заказа</th>"),
    ("<th>Position</th>", "<th>Позиция</th>"),

    # ========== СТАТИСТИКА ==========
    ("TOTAL ORDERS", "ВСЕГО ЗАКАЗОВ"),
    ("DELIVERED", "ДОСТАВЛЕНО"),
    ("REVENUE", "ВЫРУЧКА"),
    ("PRODUCTS", "ТОВАРОВ"),
    ("TOTAL VALUE", "ОБЩАЯ СТОИМОСТЬ"),
    ("LOW STOCK", "МАЛО НА СКЛАДЕ"),
    (">Products<", ">Товаров<"),
    (">Total value<", ">Общая стоимость<"),
    (">Low stock<", ">Мало на складе<"),

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
    ("<label>Amount (RUB) *</label>", "<label>Сумма (₽) *</label>"),
    ("<label>Amount", "<label>Сумма"),
    ("Your commission:", "Ваша ставка:"),
    ("Actual amount received", "Полученная сумма"),
    ("Gross:", "Итого:"),
    ("Commission:", "Комиссия:"),
    ("Expected:", "Ожидается:"),
    ("Username:", "Логин:"),
    ("Role:", "Должность:"),
    ("Telegram linked (ID:", "Telegram привязан (ID:"),
    ("Telegram linked", "Telegram привязан"),
    ("Not linked yet", "Не привязан"),
    ("New order #", "🛒 Новый заказ #"),

    # ========== МЕСТА (placeholder) ==========
    ("-- choose --", "-- выберите --"),
    ('placeholder="Name"', 'placeholder="Название"'),
    ('placeholder="Category"', 'placeholder="Категория"'),
    ('placeholder="Fee"', 'placeholder="Стоимость"'),
    ('placeholder="Free from"', 'placeholder="Бесплатно от"'),
    ('placeholder="ETA min"', 'placeholder="Время (мин)"'),
    ('placeholder="Message..."', 'placeholder="Написать сообщение..."'),
    ('placeholder="What happened?"', 'placeholder="Что случилось?"'),
    ('placeholder="Написать сообщение..."', 'placeholder="Написать сообщение..."'),

    # ========== ТЕКСТЫ "НЕТ ДАННЫХ" ==========
    (">No sales<", ">Продаж нет<"),
    (">No products<", ">Товаров нет<"),
    (">No orders<", ">Заказов нет<"),
    (">No defects<", ">Брака нет<"),
    (">No data<", ">Нет данных<"),
    (">No zones<", ">Зон нет<"),
    (">No users<", ">Пользователей нет<"),
    (">No notifications<", ">Уведомлений нет<"),
    (">No transfers<", ">Переводов нет<"),
    (">No revisions<", ">Ревизий нет<"),
    (">No images<", ">Фото нет<"),
    (">No comments<", ">Комментариев нет<"),
    (">No comments yet<", ">Комментариев пока нет<"),
    (">No subordinates yet<", ">Пока нет подчинённых<"),
    (">No missions<", ">Миссий нет<"),
    ("No subordinates yet", "Пока нет подчинённых"),

    # ========== СТАТУСЫ ==========
    (">>New<", ">>Новый<"),
    (">>Taken<", ">>Принят<"),
    (">>Delivered<", ">>Доставлен<"),
    (">>Cancelled<", ">>Отменён<"),
    (">>pending<", ">>⏳ ожидает<"),
    (">>approved<", ">>✅ одобрено<"),
    (">>rejected<", ">>❌ отклонено<"),
    (">>completed<", ">>✅ завершён<"),

    # ========== ВАЛЮТЫ ==========
    (" RUB", " ₽"),
    ("RUB</", "₽</"),
    ("RUB ", "₽ "),
    ("руб.", "₽"),
    (" руб.", " ₽"),

    # ========== РОЛИ ==========
    (">Administrator<", ">Администратор<"),
    (">ADMIN<", ">АДМИН<"),
    (">Seller<", ">Продавец<"),
    (">Mentor<", ">Наставник<"),
    (">Senior Seller<", ">Старший продавец<"),
    (">Accountant<", ">Бухгалтер<"),
    (">admin<", ">Администратор<"),

    # ========== ЛОГИН/РЕГИСТРАЦИЯ ==========
    ("Staff Login", "Вход для сотрудников"),
    ("Staff Registration", "Регистрация сотрудника"),
    ("Only admin", "Только для админа"),
    ("Only managers", "Только для руководителей"),
    ("Invalid role", "Неверная роль"),
    ("Username taken", "Логин занят"),
    ("Username already exists", "Логин уже существует"),
    ("Password too short (min 4)", "Пароль слишком короткий (мин 4)"),
    ("Wrong login or password", "Неверный логин или пароль"),
    ("Registered! Please login", "Зарегистрировано! Войдите"),
    ("Employee added!", "Сотрудник добавлен!"),
    ("Updated", "Обновлено"),
    ("Deleted", "Удалено"),
    ("Not found", "Не найдено"),
    ("Access denied", "Доступ запрещён"),
    ("Product added", "Товар добавлен"),
    ("Sale sent for approval", "Продажа отправлена на подтверждение"),
    ("Sale approved", "Продажа подтверждена"),
    ("Sale rejected, stock returned", "Продажа отклонена, товар возвращён"),
    ("Order taken", "Заказ взят"),
    ("Already taken", "Уже взят"),
    ("Error", "Ошибка"),
    ("Defect request sent", "Заявка на брак отправлена"),
    ("Defect approved", "Брак подтверждён"),
    ("Defect rejected", "Брак отклонён"),
    ("Transfer created, waiting for approval", "Перевод создан, ожидает подтверждения"),
    ("Only admin can approve this", "Только админ может подтвердить"),
    ("Transfer completed", "Перевод выполнен"),
    ("Failed - not enough stock", "Не удалось — недостаточно товара"),
    ("Transfer rejected", "Перевод отклонён"),
    ("Revision requested", "Ревизия запрошена"),
    ("Revision completed", "Ревизия завершена"),
    ("Invalid data", "Неверные данные"),
    ("Not enough stock", "Недостаточно товара"),
    ("Loaded", "Загружено"),
    ("Uploaded", "Загружено"),
    ("Zone added", "Зона добавлена"),
    ("Set as main", "Сделано главным"),
    ("Saved", "Сохранено"),
    ("Token expires", "Срок действия токена"),
    ("Cart empty", "Корзина пуста"),
    ("Added to cart", "Добавлено в корзину"),
    ("Phone already registered", "Телефон уже зарегистрирован"),
    ("Wrong phone or password", "Неверный телефон или пароль"),
    ("Order placed", "Заказ оформлен"),
    ("Бонус", "Бонус"),

    # ========== КАРТОЧКА ЗАКАЗА ==========
    ("Order #", "Заказ #"),
    ("Customer:", "Клиент:"),
    ("Address:", "Адрес:"),
    ("Total:", "Сумма:"),
    ("Status:", "Статус:"),
    ("Staff:", "Сотрудник:"),
    ("Comment:", "Комментарий:"),
    ("Chat with customer", "💬 Чат с покупателем"),
    ("Message...", "Написать сообщение..."),
    ("Take order", "🎯 Взять заказ"),
    ("Delivered", "✅ Доставить"),
    ("Already delivered", "Уже доставлен"),
    ("Payment", "Оплата"),
    ("Pending approval", "Ожидает подтверждения"),
    ("Money received", "Деньги получены"),

    # ========== КАРТОЧКА ТОВАРА ==========
    ("Price", "Цена"),
    ("In stock", "В наличии"),
    ("Out of stock", "Нет в наличии"),
    ("Add to cart", "В корзину"),

    # ========== ФИНАНСЫ ==========
    ("Total balance", "Общий баланс"),
    ("Income", "Поступление"),
    ("Expense", "Расход"),
    ("Pending", "Ожидает"),
    ("Approve", "Подтвердить"),
    ("Reject", "Отклонить"),
    ("Amount", "Сумма"),
    ("Account", "Счёт"),

    # ========== МИССИИ ==========
    ("Mission", "Миссия"),
    ("Reward", "Награда"),
    ("Progress", "Прогресс"),
    ("Completed", "Выполнено"),
    ("In progress", "В процессе"),
    ("Rejected", "Отклонено"),
    ("Pending approval", "На проверке"),
    ("Claim", "Забрать"),
]


# ============================================================
# ОБРАБОТКА
# ============================================================
def process_file(path):
    try:
        content = open(path, encoding="utf-8").read()
    except Exception:
        return False
    
    original = content
    count = 0
    
    for old, new in REPLACEMENTS:
        if old in content:
            content = content.replace(old, new)
            count += 1
    
    if content != original:
        open(path, "w", encoding="utf-8").write(content)
        return count
    return 0


total_replacements = 0
files_changed = 0
files_total = 0

for folder in ["templates", "templates/shop"]:
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if fname.endswith(".html"):
            path = os.path.join(folder, fname)
            cnt = process_file(path)
            if cnt > 0:
                files_changed += 1
                total_replacements += cnt
                print("  OK", path, "(" + str(cnt) + " замен)")
            files_total += 1

print()
print("=" * 70)
print("ФАЙЛОВ ОБРАБОТАНО:", files_total)
print("ФАЙЛОВ ИЗМЕНЕНО:", files_changed)
print("ВСЕГО ЗАМЕН:", total_replacements)
print("=" * 70)
print()

# ============================================================
# ПОИСК ОСТАВШЕГОСЯ АНГЛИЙСКОГО
# ============================================================
print("Проверка — ищем оставшийся английский...")
print()

# Ищем в тексте, который выводится пользователю (между >...<)
english_pattern = re.compile(r'>([A-Z][a-z]+(?:\s+[A-Za-z]+)+)<')
found = {}

for folder in ["templates", "templates/shop"]:
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if not fname.endswith(".html"):
            continue
        path = os.path.join(folder, fname)
        try:
            content = open(path, encoding="utf-8").read()
        except Exception:
            continue
        
        # Ищем текст между тегами
        for m in english_pattern.finditer(content):
            text = m.group(1)
            # Пропускаем то что уже содержит русские буквы
            if re.search(r'[а-яА-ЯёЁ]', text):
                continue
            # Пропускаем переменные Jinja
            if '{{' in text or '{%' in text:
                continue
            found.setdefault(text, []).append(fname)

if found:
    print("Найдены английские тексты:")
    for text in sorted(found.keys()):
        print("  '" + text + "' →", ", ".join(set(found[text])))
else:
    print("✓ Английского текста в шаблонах не найдено")

print()
print("Restart server + Ctrl+F5")