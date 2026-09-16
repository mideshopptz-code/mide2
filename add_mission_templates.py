# -*- coding: utf-8 -*-
import os

os.makedirs("templates", exist_ok=True)
os.makedirs("templates/shop", exist_ok=True)

# ============================================================
# 1. Список миссий (для админа)
# ============================================================
ADMIN_LIST = '''{% extends "base.html" %}{% block content %}
<h1>🎯 Конструктор миссий</h1>

<div class="card">
  <a href="/missions/new" class="btn btn-success">+ Создать миссию</a>
</div>

{% if pending %}
<div class="card" style="border-left:4px solid #f39c12">
  <h3>⏳ Ожидают подтверждения ({{ pending|length }})</h3>
  <table style="margin-top:12px">
    <thead><tr>
      <th>Клиент</th><th>Миссия</th><th>Награда</th>
      <th>Доказательство</th><th>Действия</th>
    </tr></thead>
    <tbody>
    {% for p in pending %}
    <tr>
      <td>{{ p.customer_name }}<br><small>{{ p.customer_phone }}</small></td>
      <td>{{ p.icon }} {{ p.title }}</td>
      <td><b>{{ p.reward_value|int }} баллов</b></td>
      <td style="font-size:12px">{{ p.proof_text or '-' }}
        {% if p.proof_url %}<br><a href="{{ p.proof_url }}" target="_blank">Ссылка →</a>{% endif %}
      </td>
      <td>
        <form method="post" action="/missions/approve/{{ p.id }}" style="display:inline">
          <input type="hidden" name="approve" value="1">
          <button class="btn btn-sm btn-success">✓</button>
        </form>
        <form method="post" action="/missions/approve/{{ p.id }}" style="display:inline">
          <input type="hidden" name="approve" value="0">
          <button class="btn btn-sm btn-danger">✗</button>
        </form>
      </td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
</div>
{% endif %}

<div class="card">
  <h3>Все миссии ({{ missions|length }})</h3>
  <table style="margin-top:12px">
    <thead><tr>
      <th>Иконка</th><th>Название</th><th>Тип</th><th>Цель</th>
      <th>Награда</th><th>Активна</th><th>Действия</th>
    </tr></thead>
    <tbody>
    {% for m in missions %}
    <tr>
      <td style="font-size:28px">{{ m.icon }}</td>
      <td>
        <b>{{ m.title }}</b><br>
        <small style="color:#7f8c8d">{{ m.description or '' }}</small>
      </td>
      <td>
        {% if m.mission_category == 'buy' %}🛒 Купить
        {% elif m.mission_category == 'subscribe' %}📱 Подписаться
        {% elif m.mission_category == 'invite' %}👥 Пригласить
        {% elif m.mission_category == 'post' %}📝 Пост
        {% elif m.mission_category == 'task' %}✅ Задание
        {% else %}{{ m.mission_category }}{% endif %}
      </td>
      <td>{{ m.target_value|int }}</td>
      <td><b style="color:#e74c3c">{{ m.reward_value|int }} б.</b></td>
      <td>{% if m.is_active %}✅{% else %}🚫{% endif %}</td>
      <td>
        <a href="/missions/{{ m.id }}/edit" class="btn btn-sm">✏️</a>
        <form method="post" action="/missions/{{ m.id }}/toggle" style="display:inline">
          <button class="btn btn-sm">{{ 'Выкл' if m.is_active else 'Вкл' }}</button>
        </form>
        <form method="post" action="/missions/{{ m.id }}/delete" style="display:inline"
              onsubmit="return confirm('Удалить миссию?')">
          <button class="btn btn-sm btn-danger">🗑️</button>
        </form>
      </td>
    </tr>
    {% else %}
    <tr><td colspan="7" style="text-align:center;padding:20px;color:#7f8c8d">
      Миссий пока нет. Создайте первую!
    </td></tr>
    {% endfor %}
    </tbody>
  </table>
</div>

{% endblock %}'''

# ============================================================
# 2. Форма создания миссии (конструктор)
# ============================================================
ADMIN_FORM = '''{% extends "base.html" %}{% block content %}
<h1>{{ '✏️ Редактировать' if mission else '🎯 Создать миссию' }}</h1>

<div class="card" style="max-width:700px;margin:auto">

<form method="post" id="missionForm">

  <label>Тип миссии *</label>
  <div class="mission-types" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:20px">
    <label class="type-card" data-type="buy">
      <input type="radio" name="mission_category" value="buy" {% if mission and mission.mission_category == 'buy' %}checked{% elif not mission %}checked{% endif %}>
      <div>
        <div style="font-size:32px">🛒</div>
        <b>Купить</b>
      </div>
    </label>
    <label class="type-card" data-type="subscribe">
      <input type="radio" name="mission_category" value="subscribe" {% if mission and mission.mission_category == 'subscribe' %}checked{% endif %}>
      <div>
        <div style="font-size:32px">📱</div>
        <b>Подписаться</b>
      </div>
    </label>
    <label class="type-card" data-type="invite">
      <input type="radio" name="mission_category" value="invite" {% if mission and mission.mission_category == 'invite' %}checked{% endif %}>
      <div>
        <div style="font-size:32px">👥</div>
        <b>Пригласить</b>
      </div>
    </label>
    <label class="type-card" data-type="post">
      <input type="radio" name="mission_category" value="post" {% if mission and mission.mission_category == 'post' %}checked{% endif %}>
      <div>
        <div style="font-size:32px">📝</div>
        <b>Пост</b>
      </div>
    </label>
    <label class="type-card" data-type="task">
      <input type="radio" name="mission_category" value="task" {% if mission and mission.mission_category == 'task' %}checked{% endif %}>
      <div>
        <div style="font-size:32px">✅</div>
        <b>Задание</b>
      </div>
    </label>
  </div>

  <label>Иконка (emoji)</label>
  <input name="icon" value="{{ mission.icon if mission else '🎯' }}" maxlength="4" style="font-size:20px">

  <label>Название миссии *</label>
  <input name="title" required value="{{ mission.title if mission else '' }}" placeholder="Купи 3 товара">

  <label>Описание</label>
  <textarea name="description" rows="2" placeholder="Что нужно сделать">{{ mission.description if mission else '' }}</textarea>

  <label>Код (уникальный, латиницей)</label>
  <input name="code" value="{{ mission.code if mission else '' }}" {% if mission %}disabled{% endif %} placeholder="buy_3_items">

  <label>Сколько раз выполнить *</label>
  <input name="target_value" type="number" min="1" value="{{ mission.target_value if mission else 1 }}" required>

  <label>💰 Награда (баллы) *</label>
  <input name="reward_value" type="number" min="1" value="{{ mission.reward_value if mission else 100 }}" required>

  <div id="url-block" style="display:none">
    <label>Ссылка (куда подписаться / куда пост)</label>
    <input name="action_url" value="{{ mission.action_url if mission else '' }}" placeholder="https://instagram.com/...">
  </div>

  <div id="platform-block" style="display:none">
    <label>Платформа</label>
    <select name="platform">
      <option value="">— выберите —</option>
      <option value="instagram" {% if mission and mission.platform == 'instagram' %}selected{% endif %}>Instagram</option>
      <option value="vk" {% if mission and mission.platform == 'vk' %}selected{% endif %}>VK</option>
      <option value="telegram" {% if mission and mission.platform == 'telegram' %}selected{% endif %}>Telegram</option>
      <option value="youtube" {% if mission and mission.platform == 'youtube' %}selected{% endif %}>YouTube</option>
      <option value="tiktok" {% if mission and mission.platform == 'tiktok' %}selected{% endif %}>TikTok</option>
      <option value="other" {% if mission and mission.platform == 'other' %}selected{% endif %}>Другое</option>
    </select>
  </div>

  <label>Подсказка для проверки</label>
  <input name="verify_hint" value="{{ mission.verify_hint if mission else '' }}" placeholder="Скинь скриншот или ссылку">

  <label>Повторяемость</label>
  <select name="repeat_type">
    <option value="once" {% if mission and mission.repeat_type == 'once' %}selected{% endif %}>Один раз</option>
    <option value="daily" {% if mission and mission.repeat_type == 'daily' %}selected{% endif %}>Ежедневно</option>
    <option value="weekly" {% if mission and mission.repeat_type == 'weekly' %}selected{% endif %}>Еженедельно</option>
    <option value="monthly" {% if mission and mission.repeat_type == 'monthly' %}selected{% endif %}>Ежемесячно</option>
  </select>

  <label style="display:flex;align-items:center;gap:10px;margin-top:20px">
    <input type="checkbox" name="requires_approval" value="1" style="width:auto"
           {% if mission and mission.requires_approval %}checked{% endif %}>
    Требуется подтверждение админом
  </label>

  <div style="margin-top:24px;display:flex;gap:12px">
    <button class="btn btn-success" type="submit" style="flex:1">
      💾 {{ 'Сохранить' if mission else 'Создать' }}
    </button>
    <a href="/missions" class="btn" style="background:#95a5a6">Отмена</a>
  </div>

</form>
</div>

<style>
.type-card{
  display:flex;align-items:center;gap:10px;
  padding:16px 12px;border:2px solid #e5e5ea;border-radius:12px;
  cursor:pointer;transition:all .3s;text-align:center;
  flex-direction:column;
}
.type-card:hover{border-color:#7c3aed;transform:translateY(-2px)}
.type-card input{display:none}
.type-card input:checked + div{color:#7c3aed}
.type-card:has(input:checked){border-color:#7c3aed;background:rgba(124,58,237,.06)}
</style>

<script>
function updateFields(){
  var cat = document.querySelector('input[name="mission_category"]:checked').value;
  var urlBlock = document.getElementById('url-block');
  var platformBlock = document.getElementById('platform-block');
  
  if(cat === 'subscribe' || cat === 'post'){
    urlBlock.style.display = 'block';
    platformBlock.style.display = 'block';
  } else {
    urlBlock.style.display = 'none';
    platformBlock.style.display = 'none';
  }
}
document.querySelectorAll('input[name="mission_category"]').forEach(function(el){
  el.addEventListener('change', updateFields);
});
updateFields();
</script>

{% endblock %}'''

# ============================================================
# 3. Страница миссий для покупателя
# ============================================================
SHOP_MISSIONS = '''{% extends "shop/base.html" %}{% block content %}

<h1>🎯 Миссии</h1>

<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(320px,1fr))">
{% for m in missions %}

  <div class="product" style="padding:0">
    <div class="product-body">
      
      <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px">
        <div style="font-size:44px">{{ m.icon }}</div>
        <div>
          <div class="product-meta" style="margin-bottom:4px">
            {% if m.mission_category == 'buy' %}🛒 КУПИТЬ
            {% elif m.mission_category == 'subscribe' %}📱 ПОДПИСАТЬСЯ
            {% elif m.mission_category == 'invite' %}👥 ПРИГЛАСИТЬ
            {% elif m.mission_category == 'post' %}📝 ПОСТ
            {% elif m.mission_category == 'task' %}✅ ЗАДАНИЕ
            {% endif %}
          </div>
          <div class="product-title" style="min-height:auto">{{ m.title }}</div>
        </div>
      </div>

      {% if m.description %}
      <p style="font-size:14px;color:#6b7280;margin-bottom:14px">{{ m.description }}</p>
      {% endif %}

      {% if m.action_url %}
      <a href="{{ m.action_url }}" target="_blank"
         style="display:block;font-size:13px;color:#7c3aed;margin-bottom:14px;word-break:break-all">
        🔗 {{ m.action_url[:60] }}{% if m.action_url|length > 60 %}...{% endif %}
      </a>
      {% endif %}

      <div style="display:flex;justify-content:space-between;margin-bottom:14px;font-size:14px">
        <span>Нужно: <b>{{ m.target_value|int }}</b></span>
        <span style="color:#ed1d36;font-weight:800">{{ m.reward_value|int }} б.</span>
      </div>

      {% if m.verify_hint %}
      <div style="background:#fff3cd;padding:10px;border-radius:8px;font-size:12px;margin-bottom:14px">
        💡 {{ m.verify_hint }}
      </div>
      {% endif %}

      {% if m.user_status == 'completed' %}
        <div style="text-align:center;color:#22c55e;font-weight:800;padding:14px">
          ✅ Выполнено · +{{ m.reward_value|int }} б.
        </div>

      {% elif m.user_status == 'pending_approval' %}
        <div style="text-align:center;color:#f39c12;font-weight:800;padding:14px">
          ⏳ На проверке
        </div>

      {% elif m.user_status == 'rejected' %}
        <form method="post" action="/shop/missions/{{ m.id }}/complete">
          <div style="color:#ed1d36;font-size:12px;margin-bottom:8px;text-align:center">
            Отклонено. Попробуйте снова
          </div>
          <input name="proof_text" placeholder="Что вы сделали">
          <input name="proof_url" placeholder="Ссылка (если есть)">
          <button class="btn btn-red" type="submit" style="width:100%">Отправить снова</button>
        </form>

      {% else %}
        <form method="post" action="/shop/missions/{{ m.id }}/complete">
          <input name="proof_text" placeholder="Комментарий (что сделали)">
          <input name="proof_url" placeholder="Ссылка / скриншот URL">
          <button class="btn btn-red" type="submit" style="width:100%">
            🚀 Выполнено
          </button>
        </form>
      {% endif %}
      
    </div>
  </div>

{% else %}
  <div class="empty-state" style="grid-column:1/-1">
    <div class="icon">🎯</div>
    <h3>Миссий пока нет</h3>
    <p>Скоро появятся интересные задания</p>
  </div>
{% endfor %}
</div>

{% endblock %}'''

# Сохраняем
with open("templates/admin_missions.html", "w", encoding="utf-8") as f:
    f.write(ADMIN_LIST)
print("OK templates/admin_missions.html")

with open("templates/admin_mission_form.html", "w", encoding="utf-8") as f:
    f.write(ADMIN_FORM)
print("OK templates/admin_mission_form.html")

with open("templates/shop/missions.html", "w", encoding="utf-8") as f:
    f.write(SHOP_MISSIONS)
print("OK templates/shop/missions.html")

print()
print("Done! Restart server.")