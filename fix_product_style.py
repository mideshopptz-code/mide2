# -*- coding: utf-8 -*-

# Читаем текущий шаблон
content = open("templates/shop/base.html", encoding="utf-8").read()

# Новые стили для карточек товаров
NEW_CSS = """
/* ==================== PRODUCT CARD V2 ==================== */
.product-title{
  font-size:20px !important;
  font-weight:900 !important;
  line-height:1.3 !important;
  letter-spacing:-.5px !important;
  color:var(--black) !important;
  margin-bottom:10px !important;
}
.product-meta{
  font-size:13px !important;
  color:var(--purple) !important;
  font-weight:700 !important;
  text-transform:uppercase !important;
  letter-spacing:1px !important;
  margin-bottom:16px !important;
}
.product-price{
  font-size:36px !important;
  font-weight:900 !important;
  color:var(--red) !important;
  letter-spacing:-1.8px !important;
  line-height:1 !important;
  display:flex !important;
  align-items:baseline !important;
  gap:4px !important;
  margin-top:auto !important;
}
.product-price .currency{
  font-size:22px !important;
  color:var(--black) !important;
  font-weight:800 !important;
  letter-spacing:0 !important;
}
.product-price .amount{
  color:var(--red) !important;
}
.product-stock{
  font-size:12px !important;
  color:var(--gray-text) !important;
  margin-top:6px !important;
  font-weight:500 !important;
}
.product-stock-low{
  color:var(--red) !important;
  font-weight:700 !important;
}
.product-seller{
  font-size:13px !important;
  color:var(--gray-text) !important;
  padding:8px 0 !important;
  border-top:1px solid var(--gray-mid) !important;
  margin-top:12px !important;
}
"""

# Вставляем перед закрывающим </style>
if ".product-title" in content and "PRODUCT CARD V2" not in content:
    content = content.replace("</style>", NEW_CSS + "\n</style>")
    open("templates/shop/base.html", "w", encoding="utf-8").write(content)
    print("OK: product styles updated")
else:
    print("already updated or no .product-title found")

# ============================================================
# Теперь обновим каталог — сделаем красивые карточки
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
      <div class="product-title">{{ p.name }}</div>
      <div class="product-meta">{{ p.category or 'Без категории' }}</div>
      <div class="product-price">
        <span class="amount">{{ "%.0f"|format(p.price) }}</span>
        <span class="currency">₽</span>
      </div>
      <div class="product-stock{% if p.quantity < 10 %} product-stock-low{% endif %}">
        {% if p.quantity > 0 %}
          В наличии: {{ p.quantity }} шт.
        {% else %}
          Нет в наличии
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
print("OK: catalog.html styled")

print()
print("Done! Restart server.")