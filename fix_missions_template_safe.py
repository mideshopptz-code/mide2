# -*- coding: utf-8 -*-

# Обновляем шаблон — используем безопасные значения
SHOP_MISSIONS = '''{% extends "shop/base.html" %}{% block content %}

<h1>🎯 Миссии</h1>

<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(340px,1fr))">
{% for m in missions %}

  {% set user_current = m.user_current if m.user_current is defined else m.current_value if m.current_value is defined else 0 %}
  {% set target = m.target_value if m.target_value is defined else 1 %}
  {% set reward = m.reward_value if m.reward_value is defined else 0 %}
  {% set progress = (user_current / target * 100)|int if target > 0 else 0 %}
  {% set remaining = target - user_current if target > user_current else 0 %}

  <div class="product" style="padding:0">
    <div class="product-body">

      <div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:14px">
        <div style="font-size:46px;line-height:1">{{ m.icon or '🎯' }}</div>
        <div style="flex:1">
          <div class="product-meta" style="margin-bottom:4px">
            {% if m.mission_category == 'buy' %}🛒 КУПИТЬ
            {% elif m.mission_category == 'subscribe' %}📱 ПОДПИСАТЬСЯ
            {% elif m.mission_category == 'invite' %}👥 ПРИГЛАСИТЬ
            {% elif m.mission_category == 'post' %}📝 ПОСТ
            {% elif m.mission_category == 'task' %}✅ ЗАДАНИЕ
            {% else %}🎯 МИССИЯ{% endif %}
          </div>
          <div class="product-title" style="min-height:auto;margin-bottom:0">{{ m.title }}</div>
        </div>
      </div>

      {% if m.description %}
      <p style="font-size:14px;color:#6b7280;margin-bottom:14px">{{ m.description }}</p>
      {% endif %}

      {% if m.action_url %}
      <a href="{{ m.action_url }}" target="_blank"
         style="display:block;font-size:13px;color:#7c3aed;margin-bottom:14px;word-break:break-all;
                padding:10px;background:rgba(124,58,237,.08);border-radius:8px">
        🔗 Открыть ссылку
      </a>
      {% endif %}

      {% if m.verify_hint %}
      <div style="background:#fff3cd;padding:10px;border-radius:8px;font-size:12px;margin-bottom:14px">
        💡 {{ m.verify_hint }}
      </div>
      {% endif %}

      <div style="background:#f8f8fc;padding:12px;border-radius:10px;margin-bottom:14px">
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px">
          <span>Прогресс</span>
          <b>{{ user_current|int }} / {{ target|int }}</b>
        </div>
        <div style="background:#e5e5ea;height:8px;border-radius:4px;overflow:hidden">
          <div style="width:{{ progress }}%;height:100%;
                      background:linear-gradient(90deg,#7c3aed,#ed1d36);
                      transition:width .4s ease"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:13px">
          <span style="color:#6b7280">
            {% if m.repeat_type == 'daily' %}🔄 Ежедневно
            {% elif m.repeat_type == 'weekly' %}🔄 Еженедельно
            {% elif m.repeat_type == 'monthly' %}🔄 Ежемесячно
            {% else %}⭐ Одноразовая{% endif %}
          </span>
          <b style="color:#ed1d36">{{ reward|int }} б.</b>
        </div>
      </div>

      {% if m.user_status == 'pending_approval' %}
        <div style="text-align:center;color:#f39c12;font-weight:800;padding:14px;
                    background:rgba(243,156,18,.1);border-radius:10px">
          ⏳ На проверке
        </div>
      {% else %}
        <form method="post" action="/shop/missions/{{ m.id }}/complete">
          {% if m.mission_category in ('subscribe', 'post') or m.requires_approval %}
          <input name="proof_text" placeholder="Комментарий (что сделали)">
          <input name="proof_url" placeholder="Ссылка на скриншот / профиль">
          {% endif %}
          <button class="btn btn-red" type="submit" style="width:100%">
            🚀 Выполнено +1
          </button>
        </form>
      {% endif %}

    </div>
  </div>

{% else %}
  <div class="empty-state" style="grid-column:1/-1">
    <div class="icon">🎉</div>
    <h3>Все миссии выполнены!</h3>
    <p>Заходи позже — скоро появятся новые</p>
    <a href="/shop" class="btn btn-red" style="margin-top:20px">К каталогу</a>
  </div>
{% endfor %}
</div>

{% endblock %}'''

with open("templates/shop/missions.html", "w", encoding="utf-8") as f:
    f.write(SHOP_MISSIONS)
print("OK: missions.html updated (safe template)")

print()
print("Now checking web_app.py for duplicate routes...")

content = open("web_app.py", encoding="utf-8").read()

# Находим все определения shop_missions
import re
matches = [m.start() for m in re.finditer(r'@app\.route\("/shop/missions"\)', content)]
print("Found", len(matches), "routes for /shop/missions")

if len(matches) > 1:
    print("  Duplicate found! Removing old one (first)...")
    # Удаляем ПЕРВЫЙ (старый) маршрут
    # Ищем начало блока — до следующего @app.route или def
    first = matches[0]
    # Находим конец первого маршрута — следующий @app.route или конец функции
    next_route = content.find("\n@app.route", first + 10)
    if next_route == -1:
        next_route = len(content)
    
    # Удаляем блок
    content = content[:first] + content[next_route+1:]
    open("web_app.py", "w", encoding="utf-8").write(content)
    print("  OK: removed old route")

print()
print("Done! Restart server.")