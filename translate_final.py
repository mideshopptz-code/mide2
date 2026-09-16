# -*- coding: utf-8 -*-
import os

print("=" * 60)
print("ФИНАЛЬНЫЙ ПЕРЕВОД")
print("=" * 60)
print()

REPLACEMENTS = [
    # ========== НОВАЯ ПРОДАЖА ==========
    ("Your commission:", "Ваша ставка:"),
    ("-- choose --", "-- выберите --"),
    ("Gross:", "Итого:"),
    ("Commission:", "Комиссия:"),
    ("Expected:", "Ожидается:"),
    ("Actual amount received", "Полученная сумма"),
    ("Send for approval", "Отправить на подтверждение"),

    # ========== ПРОФИЛЬ ==========
    ("Username:", "Логин:"),
    ("Role:", "Должность:"),
    ("Commission:", "Комиссия:"),
    ("Telegram linked (ID:", "Telegram привязан (ID:"),
    ("Telegram linked", "Telegram привязан"),
    ("Unlink", "Отвязать"),
    ("Not linked yet.", "Не привязан."),

    # ========== УВЕДОМЛЕНИЯ ==========
    ("New order #", "🛒 Новый заказ #"),
    ("New post", "Новое поступление"),

    # ========== ДАШБОРД ==========
    ("TOTAL ORDERS", "ВСЕГО ЗАКАЗОВ"),
    ("DELIVERED", "ДОСТАВЛЕНО"),
    ("REVENUE", "ВЫРУЧКА"),
    ("PRODUCT", "ТОВАР"),
    ("QTY", "КОЛ-ВО"),
    ("SELLER", "ПРОДАВЕЦ"),
    ("ORDERS", "ЗАКАЗОВ"),

    # ========== KPI ==========
    ("SALES", "ПРОДАЖ"),
    ("REVENUE", "ВЫРУЧКА"),
    ("ACCURACY", "ТОЧНОСТЬ"),
    ("SELLER", "ПРОДАВЕЦ"),

    # ========== ЗОНЫ ==========
    ("NAME", "НАЗВАНИЕ"),
    ("FEE", "СТОИМОСТЬ"),
    ("FREE FROM", "БЕСПЛАТНО ОТ"),
    ("ВРЕМЯ", "ВРЕМЯ"),

    # ========== ФОРМЫ ==========
    ("-- choose --", "-- выберите --"),
    ("-- нет --", "-- нет --"),
    ("-- No manager --", "-- Нет руководителя --"),

    # ========== КНОПКИ ==========
    ("Request", "Отправить"),
    ("Create transfer", "Создать перевод"),
    ("Send request", "Отправить заявку"),
    ("Send", "Отправить"),
    ("Открыть", "Открыть"),

    # ========== РЕВИЗИЯ ==========
    ("Кого проверить", "Кого проверить"),

    # ========== ЗАКАЗЫ ==========
    ("CUSTOMER", "КЛИЕНТ"),
    ("PHONE", "ТЕЛЕФОН"),
    ("ADDRESS", "АДРЕС"),
    ("TOTAL", "ИТОГО"),
    ("STAFF", "СОТРУДНИК"),
    ("STATUS", "СТАТУС"),

    # ========== СТАТУСЫ ==========
    (">Доставлен<", ">✅ Доставлен<"),
    (">Принят<", ">📦 Принят<"),
    (">Новый<", ">🆕 Новый<"),
    (">Отменён<", ">❌ Отменён<"),
]


def process_file(path):
    try:
        content = open(path, encoding="utf-8").read()
    except Exception:
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

for folder in ["templates", "templates/shop"]:
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if fname.endswith(".html"):
            path = os.path.join(folder, fname)
            if process_file(path):
                count += 1
                print("  OK", path)
            total += 1

print()
print("=" * 60)
print("ИЗМЕНЕНО ФАЙЛОВ:", count, "из", total)
print("=" * 60)
print()
print("Restart server + Ctrl+F5")