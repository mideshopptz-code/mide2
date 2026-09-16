# -*- coding: utf-8 -*-
import re

content = open("templates/base.html", encoding="utf-8").read()

# Найдём текущий nav
nav_match = re.search(r'<nav>(.*?)</nav>', content, re.DOTALL)
if not nav_match:
    print("ERROR: nav not found")
    exit()

old_nav = nav_match.group(0)

# Полностью новый nav с финансами
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
      <a href="/">Товары</a>
      <a href="/sales">Продажи</a>
      <a href="/orders">Заказы</a>
      <a href="/defects">Дефекты</a>
      <a href="/transfers">Переводы</a>
      {% if user.role in ('admin','senior_seller','mentor') %}
        <a href="/team">Команда</a>
        <a href="/revisions">Ревизии</a>
      {% endif %}
      {% if user.role == 'admin' %}
        <a href="/staff">Сотрудники</a>
        <a href="/missions">Миссии</a>
      {% endif %}
      <a href="/dashboard">Панель управления</a>
      {% if user.role in ('admin','senior_seller','mentor') %}
        <a href="/kpi">KPI</a>
      {% endif %}
      {% if user.role == 'admin' %}
        <a href="/zones">Зоны</a>
      {% endif %}
      {% if user.role in ('admin', 'accountant') %}
        <a href="/finance">💰 Финансы</a>
      {% endif %}
      <a href="/profile">Профиль</a>
      <a href="/notifications">Уведомления</a>
    {% endif %}
    <span style="margin-left:auto;font-size:13px">
      {{ user.full_name or user.username }}
      <span class="role-badge role-{{ user.role }}">{{ user.role }}</span>
    </span>
    <a href="/logout">Выход</a>
  {% endif %}
</nav>'''

content = content.replace(old_nav, NEW_NAV)
open("templates/base.html", "w", encoding="utf-8").write(content)

# Проверка
c = open("templates/base.html", encoding="utf-8").read()
print("Check:")
print("  /finance:", "/finance" in c)
print("  /admin/bank-accounts:", "/admin/bank-accounts" in c)
print("  Финансы:", "Финансы" in c)
print()
print("Done! Restart server + Ctrl+F5 in browser.")