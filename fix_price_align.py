# -*- coding: utf-8 -*-

content = open("templates/shop/base.html", encoding="utf-8").read()

# Новые стили цен — с отступом и правильной вёрсткой
NEW_CSS = """
/* ==================== PRICE FIX V3 ==================== */
.product-body{
  padding:24px 24px 28px 24px !important;
}
.product-price{
  font-size:38px !important;
  font-weight:900 !important;
  letter-spacing:-2px !important;
  line-height:1 !important;
  display:flex !important;
  align-items:baseline !important;
  gap:6px !important;
  padding:16px 0 12px 0 !important;
  margin:0 !important;
  border-top:2px solid var(--gray-mid) !important;
  margin-top:16px !important;
}
.product-price .amount{
  color:var(--red) !important;
  font-family:'Inter','Segoe UI',sans-serif !important;
  font-variant-numeric:tabular-nums !important;
}
.product-price .currency{
  font-size:24px !important;
  color:var(--red) !important;
  font-weight:800 !important;
  letter-spacing:-.5px !important;
  opacity:.85 !important;
}
.product-title{
  font-size:19px !important;
  font-weight:800 !important;
  line-height:1.35 !important;
  letter-spacing:-.4px !important;
  margin-bottom:12px !important;
  color:var(--black) !important;
  min-height:52px !important;
  display:-webkit-box !important;
  -webkit-line-clamp:2 !important;
  -webkit-box-orient:vertical !important;
  overflow:hidden !important;
}
.product-meta{
  font-size:11px !important;
  color:var(--purple) !important;
  font-weight:700 !important;
  text-transform:uppercase !important;
  letter-spacing:1.2px !important;
  margin-bottom:8px !important;
  display:inline-block !important;
  background:rgba(124,58,237,.08) !important;
  padding:4px 10px !important;
  border-radius:6px !important;
}
.product-stock{
  font-size:12px !important;
  color:var(--gray-text) !important;
  margin-top:10px !important;
  font-weight:500 !important;
  padding:6px 0 !important;
}
.product-stock-low{
  color:var(--red) !important;
  font-weight:800 !important;
}
.product-seller{
  font-size:12px !important;
  color:var(--gray-text) !important;
  padding:10px 0 0 0 !important;
  border-top:1px solid var(--gray-mid) !important;
  margin-top:12px !important;
  display:flex !important;
  align-items:center !important;
  gap:6px !important;
}
.product-price-wrap{
  display:flex !important;
  align-items:center !important;
  justify-content:space-between !important;
  width:100% !important;
}
"""

# Заменяем старый блок (если есть)
if "PRICE FIX V3" not in content:
    # Находим место перед </style> и вставляем
    content = content.replace("</style>", NEW_CSS + "\n</style>")
    open("templates/shop/base.html", "w", encoding="utf-8").write(content)
    print("OK: price align fixed")
else:
    print("already fixed")

# ============================================================
# Обновим catalog.html — структура цены с обёрткой
# ============================================================
CATALOG = '''{% extends "shop/base.html" %}{% block content %}

<div class="hero">
  <h2>MIDE<span style="color:var(--purple-light)">.</span></h2>
  <p>Премиальный магазин товаров повседневного спроса</p>
</div>

<h1>Каталог товаров</h1>

<div class="grid">
{% for p in products %}
  <div class="product">
    <a href="/shop/product/{{ p.id }}" style="text-decoration:none;color:inherit">
      <div class="product-img">
        {% if p.main_image %}
          <img src="/static/uploads/{{ p.main_image }}" alt="{{ p.name }}">
        {% else %}
          📦
        {% endif %}
      </div>
    </a>
    <div class="product-body">
      <div class="product-meta">{{ p.category or 'Без категории' }}</div>
      <div class="product-title">{{ p.name }}</div>

      <div class="product-price">
        <span class="amount">{{ "%.0f"|format(p.price) }}</span>
        <span class="currency">₽</span>
      </div>

      <div class="product-stock{% if p.quantity < 10 %} product-stock-low{% endif %}">
        {% if p.quantity > 0 %}
          ✓ В наличии: {{ p.quantity }} шт.
        {% else %}
          ✗ Нет в наличии
        {% endif %}
      </div>

      <div class="product-seller">🏪 {{ p.seller_name or p.seller_username }}</div>

      {% if p.quantity > 0 %}
      <form method="post" action="/shop/cart/add/{{ p.id }}" style="margin-top:14px">
        <input type="hidden" name="quantity" value="1">
        <button class="btn btn-red" type="submit" style="width:100%">
          🛒 В корзину
        </button>
      </form>
      {% else %}
      <button class="btn" disabled style="width:100%;margin-top:14px;opacity:.5;cursor:not-allowed">
        Нет в наличии
      </button>
      {% endif %}
    </div>
  </div>
{% else %}
  <div class="empty-state" style="grid-column:1/-1">
    <div class="icon">📦</div>
    <h3>Товаров пока нет</h3>
    <p>Заходите позже — мы пополняем ассортимент</p>
  </div>
{% endfor %}
</div>

{% endblock %}'''

with open("templates/shop/catalog.html", "w", encoding="utf-8") as f:
    f.write(CATALOG)
print("OK: catalog updated")

print()
print("Done! Restart server.")