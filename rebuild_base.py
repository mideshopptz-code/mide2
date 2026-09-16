# -*- coding: utf-8 -*-

BASE = '''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{% block title %}MIDE{% endblock %}</title>
<style>
:root{
  --black:#000;--white:#fff;--purple:#7c3aed;--purple-dark:#5b21a6;
  --purple-light:#a78bfa;--red:#ed1d36;--red-dark:#b91c1c;
  --gray:#f8f8fc;--gray-mid:#e5e5ea;--gray-text:#6b7280;
  --radius:18px;--radius-sm:12px;
  --shadow-md:0 4px 16px rgba(0,0,0,.08);
  --shadow-lg:0 12px 32px rgba(124,58,237,.15);
  --shadow-xl:0 24px 60px rgba(124,58,237,.25);
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:-apple-system,'Segoe UI',Roboto,sans-serif;background:var(--white);color:var(--black);line-height:1.7;-webkit-font-smoothing:antialiased}

nav{background:rgba(255,255,255,.95);backdrop-filter:blur(14px);border-bottom:1px solid var(--gray-mid);position:sticky;top:0;z-index:100}
.nav-inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;gap:10px;padding:18px 24px}
.logo{font-size:32px;font-weight:900;color:var(--black);text-decoration:none;letter-spacing:-1.8px;margin-right:26px;transition:transform .3s}
.logo:hover{transform:scale(1.04)}
.logo-dot{color:var(--purple);transition:color .3s}
.logo:hover .logo-dot{color:var(--red)}
nav a.nav-link{color:var(--black);text-decoration:none;padding:12px 20px;border-radius:var(--radius-sm);font-size:15px;font-weight:600;transition:all .3s}
nav a.nav-link:hover{background:var(--purple);color:var(--white);transform:translateY(-2px);box-shadow:var(--shadow-md)}
.cart-btn{margin-left:auto;background:var(--black);color:var(--white);padding:12px 26px;border-radius:var(--radius-sm);text-decoration:none;font-weight:700;font-size:14px;transition:all .3s;display:flex;align-items:center;gap:8px}
.cart-btn:hover{background:var(--purple);transform:translateY(-2px);box-shadow:var(--shadow-lg)}

.container{max-width:1200px;margin:0 auto;padding:36px 24px}
h1{font-size:44px;font-weight:900;letter-spacing:-2px;margin-bottom:32px;color:var(--black)}
h2{font-size:32px;font-weight:900;letter-spacing:-1px;margin-bottom:16px}
h3{font-size:22px;font-weight:800;margin-bottom:12px}

.card{background:var(--white);border:1px solid var(--gray-mid);border-radius:var(--radius);padding:28px;margin-bottom:24px;transition:all .4s}
.card:hover{box-shadow:var(--shadow-lg);transform:translateY(-3px);border-color:var(--purple-light)}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:14px 30px;background:var(--purple);color:var(--white);border:none;border-radius:var(--radius-sm);font-size:15px;font-weight:700;cursor:pointer;text-decoration:none;transition:all .3s;position:relative;overflow:hidden}
.btn::before{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.3),transparent);transition:left .6s}
.btn:hover::before{left:100%}
.btn:hover{background:var(--purple-dark);transform:translateY(-3px);box-shadow:var(--shadow-lg)}
.btn:active{transform:translateY(-1px)}
.btn-red{background:var(--red)}
.btn-red:hover{background:var(--red-dark)}
.btn-black{background:var(--black)}
.btn-black:hover{background:var(--purple)}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:28px}

.product{background:var(--white);border:1px solid var(--gray-mid);border-radius:var(--radius);overflow:hidden;transition:all .5s;display:flex;flex-direction:column}
.product:hover{transform:translateY(-10px);box-shadow:var(--shadow-xl);border-color:var(--purple)}
.product-img{width:100%;height:240px;background:linear-gradient(135deg,var(--gray),var(--gray-mid));display:flex;align-items:center;justify-content:center;font-size:80px;color:var(--gray-text);overflow:hidden}
.product-img img{width:100%;height:100%;object-fit:cover;transition:transform .6s}
.product:hover .product-img img{transform:scale(1.08)}
.product-body{padding:24px;flex:1;display:flex;flex-direction:column}
.product-meta{font-size:11px;color:var(--purple);font-weight:800;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px}
.product-title{font-size:20px;font-weight:900;line-height:1.3;letter-spacing:-.5px;margin-bottom:14px;color:var(--black);min-height:52px}
.product-seller{font-size:12px;color:var(--gray-text);font-weight:500;padding-bottom:14px;margin:0}
.product-price{display:flex;align-items:baseline;gap:4px;padding:0;margin:0 0 14px 0;font-size:38px;font-weight:900;line-height:1;letter-spacing:-2px}
.product-price .amount{color:var(--red);font-variant-numeric:tabular-nums}
.product-price .currency{font-size:22px;color:var(--red);font-weight:800;opacity:.75}
.product-stock{font-size:13px;color:var(--gray-text);font-weight:600;margin-bottom:14px}
.product-stock-low{color:var(--red)}

input,select,textarea{width:100%;padding:16px 20px;border:2px solid var(--gray-mid);border-radius:var(--radius-sm);font-size:15px;margin-bottom:16px;font-family:inherit;transition:all .3s;background:var(--white)}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--purple);box-shadow:0 0 0 4px rgba(124,58,237,.12);transform:translateY(-1px)}
label{display:block;font-size:14px;font-weight:700;color:var(--black);margin-bottom:8px}

.flash{padding:16px 22px;border-radius:var(--radius-sm);margin-bottom:20px;font-weight:600;animation:slideIn .4s}
.flash.success{background:#dcfce7;color:#166534;border-left:5px solid #22c55e}
.flash.error{background:#fee2e2;color:#991b1b;border-left:5px solid var(--red)}

table{width:100%;border-collapse:collapse}
th,td{padding:16px;text-align:left;border-bottom:1px solid var(--gray-mid)}
th{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:var(--gray-text);font-weight:700;background:var(--gray)}
tr{transition:background .2s}
tr:hover{background:var(--gray)}

.hero{background:linear-gradient(135deg,var(--black) 0%,var(--purple-dark) 100%);color:var(--white);padding:90px 40px;border-radius:28px;margin-bottom:48px;text-align:center;position:relative;overflow:hidden;animation:fadeIn .8s}
.hero::before{content:'';position:absolute;top:-30%;right:-15%;width:500px;height:500px;background:radial-gradient(circle,rgba(237,29,54,.25) 0%,transparent 70%);animation:float 8s infinite ease-in-out}
.hero::after{content:'';position:absolute;bottom:-30%;left:-15%;width:500px;height:500px;background:radial-gradient(circle,rgba(124,58,237,.3) 0%,transparent 70%);animation:float 10s infinite ease-in-out reverse}
.hero h2{font-size:58px;font-weight:900;letter-spacing:-3px;margin-bottom:16px;position:relative;z-index:1}
.hero p{font-size:20px;opacity:.92;position:relative;z-index:1;font-weight:500}

.badge{display:inline-block;background:var(--purple);color:var(--white);font-size:11px;font-weight:700;padding:5px 12px;border-radius:20px;text-transform:uppercase;letter-spacing:.8px}
.badge-red{background:var(--red)}
.badge-black{background:var(--black)}

.empty-state{text-align:center;padding:100px 20px;color:var(--gray-text);animation:fadeIn .5s}
.empty-state .icon{font-size:90px;margin-bottom:20px;opacity:.5}

@keyframes slideIn{from{opacity:0;transform:translateY(-12px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0;transform:scale(.98)}to{opacity:1;transform:scale(1)}}
@keyframes float{0%,100%{transform:translate(0,0) rotate(0)}50%{transform:translate(-24px,24px) rotate(8deg)}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(124,58,237,.7)}50%{box-shadow:0 0 0 12px rgba(124,58,237,0)}}
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/shop" class="logo">MIDE<span class="logo-dot">.</span></a>
    <a href="/shop" class="nav-link">Каталог</a>
    {% if customer %}
    <a href="/shop/missions" class="nav-link">Миссии</a>
    <a href="/shop/my-orders" class="nav-link">Заказы</a>
    <a href="/shop/bonus" class="nav-link">Бонус</a>
    {% else %}
    <a href="/shop/login" class="nav-link">Вход</a>
    <a href="/shop/register" class="nav-link">Регистрация</a>
    {% endif %}
    <a href="/shop/cart" class="cart-btn">🛒 Корзина</a>
  </div>
</nav>

<div class="container">
  {% with messages = get_flashed_messages(with_categories=true) %}
  {% for cat,msg in messages %}
  <div class="flash {{cat}}">{{msg}}</div>
  {% endfor %}
  {% endwith %}

  {% block content %}{% endblock %}
</div>

<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<script>
var socket = io();
socket.on('customer_notification', function(d){
  alert(d.title + '\n' + (d.body || ''));
});
</script>
</body>
</html>'''

with open("templates/shop/base.html", "w", encoding="utf-8") as f:
    f.write(BASE)
print("OK: base.html rebuilt")

# И каталог
CATALOG = '''{% extends "shop/base.html" %}{% block content %}

<div class="hero">
  <h2>MIDE<span style="color:var(--purple-light)">.</span></h2>
  <p>Премиальный магазин товаров повседневного спроса</p>
</div>

<h1>Каталог товаров</h1>

<div class="grid">
{% for p in products %}
  <div class="product">
    <div class="product-img">
      {% if p.main_image %}
        <img src="/static/uploads/{{ p.main_image }}" alt="{{ p.name }}">
      {% else %}
        📦
      {% endif %}
    </div>
    <div class="product-body">
      <div class="product-meta">{{ p.category or 'Категория' }}</div>
      <div class="product-title">{{ p.name }}</div>
      <div class="product-seller">🏪 {{ p.seller_name or p.seller_username }}</div>

      <div class="product-price">
        <span class="amount">{{ "%.0f"|format(p.price) }}</span>
        <span class="currency">₽</span>
      </div>

      <div class="product-stock{% if p.quantity < 10 %} product-stock-low{% endif %}">
        {% if p.quantity > 0 %}✓ В наличии: {{ p.quantity }} шт.{% else %}✗ Нет в наличии{% endif %}
      </div>

      {% if p.quantity > 0 %}
      <form method="post" action="/shop/cart/add/{{ p.id }}">
        <input type="hidden" name="quantity" value="1">
        <button class="btn btn-red" type="submit" style="width:100%">🛒 В корзину</button>
      </form>
      {% else %}
      <button class="btn" disabled style="width:100%;opacity:.4;cursor:not-allowed">Нет в наличии</button>
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
print("OK: catalog.html rebuilt")
print()
print("Done! Restart server + Ctrl+F5 in browser.")