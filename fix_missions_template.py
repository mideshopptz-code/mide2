# -*- coding: utf-8 -*-

SHOP_MISSIONS = '''{% extends "shop/base.html" %}{% block content %}

<h1>🎯 Миссии</h1>

<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(340px,1fr))">
{% for m in missions %}

  <div class="product" style="padding:0">
    <div class="product-body">

      <div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:14px">
        <div style="font-size:46px;line-height:1">{{ m.icon }}</div>
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

      {# ============ ПРОГРЕСС ============ #}
      <div style="background:#f8f8fc;padding:12px;border-radius:10px;margin-bottom:14px">
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px">
          <span>Прогресс</span>
          <b>{{ m.user_current|int }} / {{ m.target_value|int }}</b>
        </div>
        <div style="background:#e5e5ea;height:8px;border-radius:4px;overflow:hidden">
          <div style="width:{{ m.progress_percent }}%;height:100%;
                      background:linear-gradient(90deg,#7c3aed,#ed1d36);
                      transition:width .4s ease"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:13px">
          <span style="color:#6b7280">
            {% if m.repeat_type == 'daily' %}🔄 Обновляется ежедневно
            {% elif m.repeat_type == 'weekly' %}🔄 Обновляется еженедельно
            {% elif m.repeat_type == 'monthly' %}🔄 Обновляется ежемесячно
            {% else %}⭐ Одноразовая{% endif %}
          </span>
          <b style="color:#ed1d36">{{ m.reward_value|int }} б.</b>
        </div>
      </div>

      {% if m.user_status == 'pending_approval' %}
        <div style="text-align:center;color:#f39c12;font-weight:800;padding:14px;
                    background:rgba(243,156,18,.1);border-radius:10px">
          ⏳ На проверке
        </div>

      {% elif m.remaining > 0 %}
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
    <p>Заходи позже — скоро появятся новые задания</p>
    <a href="/shop" class="btn btn-red" style="margin-top:20px">К каталогу</a>
  </div>
{% endfor %}
</div>

{% endblock %}'''

with open("templates/shop/missions.html", "w", encoding="utf-8") as f:
    f.write(SHOP_MISSIONS)
print("OK templates/shop/missions.html")
print()
print("Done! Restart server.")