# -*- coding: utf-8 -*-
import os

print("=" * 60)
print("ПОСЛЕДНИЕ ПЕРЕВОДЫ")
print("=" * 60)
print()

REPLACEMENTS = [
    # Из отчёта
    ("Cart is empty", "Корзина пуста"),
    ("Chat with staff", "💬 Чат с продавцом"),
    ("Complete revision", "✅ Завершить ревизию"),
    ("Enter actual quantities", "Введите фактические остатки"),
    ("Get code", "Получить код"),
    ("Go to catalog", "Перейти в каталог"),
    ("Login to place an order", "Войдите чтобы оформить заказ"),
    ("My Orders", "📋 Мои заказы"),
    ("My bonus points", "🎁 Мои бонусы"),
    ("Result comment", "Комментарий к результату"),
    ("Spend points at checkout", "Списать баллы при заказе"),
    ("Stock value", "Стоимость склада"),
    ("Total orders", "Всего заказов"),

    # Дополнительно
    ("Login", "Вход"),
    ("Register", "Регистрация"),
    ("Password", "Пароль"),
    ("Hello,", "Привет,"),
    ("Hello", "Привет"),
    ("Welcome", "Добро пожаловать"),
    ("Total:", "Итого:"),
    ("Balance", "Баланс"),
    ("Points", "Баллов"),
    ("Bonus", "Бонус"),
    ("Quantity", "Количество"),
    ("Comment", "Комментарий"),
    ("Reason", "Причина"),
    ("Status", "Статус"),
    ("Amount", "Сумма"),
    ("Category", "Категория"),
    ("Price", "Цена"),
    ("Name", "Название"),
    ("Product", "Товар"),
    ("Products", "Товары"),
    ("Orders", "Заказы"),
    ("Sales", "Продажи"),
    ("Defects", "Брак"),
    ("Transfers", "Переводы"),
    ("Team", "Команда"),
    ("Revisions", "Ревизии"),
    ("Employees", "Сотрудники"),
    ("Missions", "Миссии"),
    ("Dashboard", "Панель управления"),
    ("Zones", "Зоны"),
    ("Profile", "Профиль"),
    ("Notifications", "Уведомления"),
    ("Logout", "Выход"),
    ("Welcome to MIDE", "Добро пожаловать в MIDE"),
    ("Premium shop", "Премиальный магазин"),
    ("Add to cart", "В корзину"),
    ("Checkout", "Оформить заказ"),
    ("Order placed", "Заказ оформлен"),
    ("Place order", "Оформить заказ"),
    ("Delivery address", "Адрес доставки"),
    ("Catalog", "Каталог"),
    ("Shop", "Магазин"),
    ("Cart", "Корзина"),
    ("Login", "Войти"),
    ("Register", "Зарегистрироваться"),
    ("Logout", "Выйти"),
    ("Order", "Заказ"),
    ("Delivery", "Доставка"),
    ("Address", "Адрес"),
    ("Phone", "Телефон"),
    ("Customer", "Клиент"),
    ("Seller", "Продавец"),
    ("Staff", "Сотрудник"),
    ("Total", "Итого"),
    ("Actions", "Действия"),
    ("Created", "Создано"),
    ("Updated", "Обновлено"),
    ("Role", "Должность"),
    ("Commission", "Комиссия"),
    ("Rate", "Ставка"),
    ("Save", "Сохранить"),
    ("Cancel", "Отмена"),
    ("Delete", "Удалить"),
    ("Edit", "Изменить"),
    ("View", "Просмотр"),
    ("Open", "Открыть"),
    ("Close", "Закрыть"),
    ("Add", "Добавить"),
    ("Send", "Отправить"),
    ("Back", "Назад"),
    ("Next", "Далее"),
    ("Yes", "Да"),
    ("No", "Нет"),
    ("OK", "OK"),
    ("Search", "Поиск"),
    ("Find", "Найти"),
    ("Filter", "Фильтр"),
    ("All", "Все"),
    ("None", "Нет"),
    ("Show", "Показать"),
    ("Hide", "Скрыть"),
    ("Print", "Печать"),
    ("Download", "Скачать"),
    ("Upload", "Загрузить"),
    ("Image", "Изображение"),
    ("Photo", "Фото"),
    ("User", "Пользователь"),
    ("Admin", "Админ"),
    ("Manager", "Руководитель"),
    ("Mentor", "Наставник"),
    ("Accountant", "Бухгалтер"),
    ("Director", "Директор"),
    ("Owner", "Владелец"),
    ("New", "Новый"),
    ("Old", "Старый"),
    ("Active", "Активный"),
    ("Inactive", "Неактивный"),
    ("Enabled", "Включено"),
    ("Disabled", "Отключено"),
    ("Pending", "Ожидает"),
    ("Approved", "Одобрено"),
    ("Rejected", "Отклонено"),
    ("Cancelled", "Отменено"),
    ("Completed", "Завершено"),
    ("Failed", "Ошибка"),
    ("Success", "Успешно"),
    ("Error", "Ошибка"),
    ("Warning", "Внимание"),
    ("Info", "Информация"),
    ("Hello world", "Привет мир"),
]


def process_file(path):
    try:
        content = open(path, encoding="utf-8").read()
    except Exception:
        return 0
    
    original = content
    count = 0
    
    for old, new in REPLACEMENTS:
        # Заменяем ТОЛЬКО между тегами и в тексте
        # Не трогаем атрибуты (id, class, href, src и т.д.)
        
        # Заменяем текст между > и <
        pattern = r'>' + re.escape(old) + r'<'
        if re.search(pattern, content):
            content = re.sub(pattern, '>' + new + '<', content)
            count += 1
        
        # Заменяем в placeholder="..."
        pattern2 = r'placeholder="' + re.escape(old) + r'"'
        if re.search(pattern2, content):
            content = re.sub(pattern2, 'placeholder="' + new + '"', content)
            count += 1
        
        # Заменяем в value="..."
        pattern3 = r'value="' + re.escape(old) + r'"'
        if re.search(pattern3, content):
            content = re.sub(pattern3, 'value="' + new + '"', content)
            count += 1
    
    if content != original:
        open(path, "w", encoding="utf-8").write(content)
        return count
    return 0


import re

total = 0
files = 0

for folder in ["templates", "templates/shop"]:
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if fname.endswith(".html"):
            path = os.path.join(folder, fname)
            cnt = process_file(path)
            if cnt > 0:
                files += 1
                total += cnt
                print("  OK", path, "(" + str(cnt) + " замен)")

print()
print("=" * 60)
print("ФАЙЛОВ:", files, "| ЗАМЕН:", total)
print("=" * 60)
print()

# Проверка
print("Проверка английского...")
english_pattern = re.compile(r'>([A-Z][a-z]+(?:\s+[A-Za-z]+)*)<')
found = {}

for folder in ["templates", "templates/shop"]:
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if not fname.endswith(".html"):
            continue
        try:
            content = open(os.path.join(folder, fname), encoding="utf-8").read()
        except Exception:
            continue
        
        for m in english_pattern.finditer(content):
            text = m.group(1)
            if re.search(r'[а-яА-ЯёЁ]', text):
                continue
            if '{{' in text or '{%' in text:
                continue
            if text in ['OK', 'ID', 'KPI', 'MIDE', 'Telegram', 'Instagram', 'YouTube', 'VK', 'TikTok']:
                continue
            found.setdefault(text, []).append(fname)

if found:
    print()
    print("Осталось английского:")
    for text in sorted(found.keys()):
        print("  '" + text + "' →", ", ".join(set(found[text])))
else:
    print()
    print("✓ ВСЁ ПО-РУССКИ!")

print()
print("Restart server + Ctrl+F5")