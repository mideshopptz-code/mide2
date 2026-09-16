# -*- coding: utf-8 -*-
import os

os.makedirs("static/uploads", exist_ok=True)

# ============================================================
# 1. БАЗОВЫЙ ШАБЛОН МАГАЗИНА (красивый)
# ============================================================
SHOP_BASE = '''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{% block title %}MIDE{% endblock %}</title>
<style>
:root{
  --black:#000;
  --white:#fff;
  --purple:#7c3aed;
  --purple-dark:#5b21a6;
  --purple-light:#a78bfa;
  --red:#ed1d36;
  --red-dark:#b91c1c;
  --gray:#f8f8fc;
  --gray-mid:#e5e5ea;
  --gray-text:#6b7280;
  --radius:18px;
  --radius-sm:12px;
  --shadow-sm:0 1px 3px rgba(0,0,0,.06);
  --shadow-md:0 4px 16px rgba(0,0,0,.08);
  --shadow-lg:0 12px 32px rgba(124,58,237,.15);
  --shadow-xl:0 24px 60px rgba(124,58,237,.25);
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  font-family:-apple-system,'Segoe UI',Roboto,sans-serif;
  background:var(--white);
  color:var(--black);
  line-height:1.7;
  -webkit-font-smoothing:antialiased;
}
body::selection{background:var(--purple);color:var(--white)}

/* ===================== NAV ===================== */
nav{
  background:rgba(255,255,255,.95);
  backdrop-filter:blur(14px);
  border-bottom:1px solid var(--gray-mid);
  position:sticky;top:0;z-index:100;
}
.nav-inner{
  max-width:1200px;margin:0 auto;
  display:flex;align-items:center;gap:10px;
  padding:18px 24px;
}
.logo{
  font-size:32px;font-weight:900;
  color:var(--black);text-decoration:none;
  letter-spacing:-1.8px;margin-right:26px;
  transition:all .3s cubic-bezier(.4,0,.2,1);
}
.logo:hover{transform:scale(1.04)}
.logo-dot{color:var(--purple);transition:color .3s}
.logo:hover .logo-dot{color:var(--red)}
nav a.nav-link{
  color:var(--black);text-decoration:none;
  padding:12px 20px;border-radius:var(--radius-sm);
  font-size:15px;font-weight:600;
  transition:all .3s cubic-bezier(.4,0,.2,1);
  position:relative;
}
nav a.nav-link:hover{
  background:var(--purple);color:var(--white);
  transform:translateY(-2px);
  box-shadow:var(--shadow-md);
}
.cart-btn{
  margin-left:auto;
  background:var(--black);color:var(--white);
  padding:12px 26px;border-radius:var(--radius-sm);
  text-decoration:none;font-weight:700;font-size:14px;
  transition:all .3s cubic-bezier(.4,0,.2,1);
  display:flex;align-items:center;gap:8px;
}
.cart-btn:hover{
  background:var(--purple);
  transform:translateY(-2px);
  box-shadow:var(--shadow-lg);
}

/* ===================== CONTAINER ===================== */
.container{max-width:1200px;margin:0 auto;padding:36px 24px}
h1{
  font-size:44px;font-weight:900;
  letter-spacing:-2px;margin-bottom:32px;
  background:linear-gradient(135deg,var(--black),var(--purple));
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  background-clip:text;
}
h2{font-size:32px;font-weight:900;letter-spacing:-1px;margin-bottom:16px}
h3{font-size:22px;font-weight:800;margin-bottom:12px}

/* ===================== CARDS ===================== */
.card{
  background:var(--white);
  border:1px solid var(--gray-mid);
  border-radius:var(--radius);
  padding:28px;margin-bottom:24px;
  transition:all .4s cubic-bezier(.4,0,.2,1);
}
.card:hover{
  box-shadow:var(--shadow-lg);
  transform:translateY(-3px);
  border-color:var(--purple-light);
}

/* ===================== BUTTONS ===================== */
.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:8px;
  padding:14px 30px;
  background:var(--purple);color:var(--white);
  border:none;border-radius:var(--radius-sm);
  font-size:15px;font-weight:700;
  cursor:pointer;text-decoration:none;
  transition:all .3s cubic-bezier(.4,0,.2,1);
  position:relative;overflow:hidden;
}
.btn::before{
  content:'';
  position:absolute;top:0;left:-100%;
  width:100%;height:100%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.3),transparent);
  transition:left .6s;
}
.btn:hover::before{left:100%}
.btn:hover{
  background:var(--purple-dark);
  transform:translateY(-3px);
  box-shadow:var(--shadow-lg);
}
.btn:active{transform:translateY(-1px)}
.btn-red{background:var(--red)}
.btn-red:hover{background:var(--red-dark)}
.btn-black{background:var(--black)}
.btn-black:hover{background:var(--purple)}

/* ===================== PRODUCTS GRID ===================== */
.grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  gap:28px;
}
.product{
  background:var(--white);
  border:1px solid var(--gray-mid);
  border-radius:var(--radius);
  overflow:hidden;
  transition:all .5s cubic-bezier(.4,0,.2,1);
  display:flex;flex-direction:column;
}
.product:hover{
  transform:translateY(-10px);
  box-shadow:var(--shadow-xl);
  border-color:var(--purple);
}
.product-img{
  width:100%;height:240px;
  background:linear-gradient(135deg,var(--gray),var(--gray-mid));
  display:flex;align-items:center;justify-content:center;
  font-size:80px;color:var(--gray-text);
  overflow:hidden;position:relative;
}
.product-img img{
  width:100%;height:100%;object-fit:cover;
  transition:transform .6s cubic-bezier(.4,0,.2,1);
}
.product:hover .product-img img{transform:scale(1.08)}
.product-body{padding:24px;flex:1;display:flex;flex-direction:column}
.product-title{
  font-size:17px;font-weight:800;
  margin-bottom:8px;letter-spacing:-.4px;
}
.product-meta{font-size:13px;color:var(--gray-text);margin-bottom:16px}
.product-price{
  font-size:30px;font-weight:900;
  color:var(--red);margin-top:auto;
  letter-spacing:-1.2px;
  transition:transform .3s;
}
.product:hover .product-price{transform:scale(1.05)}

/* ===================== FORMS ===================== */
input,select,textarea{
  width:100%;padding:16px 20px;
  border:2px solid var(--gray-mid);
  border-radius:var(--radius-sm);
  font-size:15px;margin-bottom:16px;
  font-family:inherit;
  transition:all .3s cubic-bezier(.4,0,.2,1);
  background:var(--white);
}
input:focus,select:focus,textarea:focus{
  outline:none;
  border-color:var(--purple);
  box-shadow:0 0 0 4px rgba(124,58,237,.12);
  transform:translateY(-1px);
}
label{
  display:block;font-size:14px;font-weight:700;
  color:var(--black);margin-bottom:8px;
}

/* ===================== FLASH ===================== */
.flash{
  padding:16px 22px;border-radius:var(--radius-sm);
  margin-bottom:20px;font-weight:600;
  animation:slideIn .4s cubic-bezier(.4,0,.2,1);
}
.flash.success{background:#dcfce7;color:#166534;border-left:5px solid #22c55e}
.flash.error{background:#fee2e2;color:#991b1b;border-left:5px solid var(--red)}

/* ===================== TABLES ===================== */
table{width:100%;border-collapse:collapse}
th,td{padding:16px;text-align:left;border-bottom:1px solid var(--gray-mid)}
th{
  font-size:12px;text-transform:uppercase;
  letter-spacing:1px;color:var(--gray-text);
  font-weight:700;background:var(--gray);
}
tr{transition:background .2s}
tr:hover{background:var(--gray)}

/* ===================== HERO ===================== */
.hero{
  background:linear-gradient(135deg,var(--black) 0%,var(--purple-dark) 100%);
  color:var(--white);
  padding:90px 40px;
  border-radius:28px;
  margin-bottom:48px;
  text-align:center;
  position:relative;overflow:hidden;
  animation:fadeIn .8s ease;
}
.hero::before{
  content:'';
  position:absolute;top:-30%;right:-15%;
  width:500px;height:500px;
  background:radial-gradient(circle,rgba(237,29,54,.25) 0%,transparent 70%);
  animation:float 8s infinite ease-in-out;
}
.hero::after{
  content:'';
  position:absolute;bottom:-30%;left:-15%;
  width:500px;height:500px;
  background:radial-gradient(circle,rgba(124,58,237,.3) 0%,transparent 70%);
  animation:float 10s infinite ease-in-out reverse;
}
.hero h2{
  font-size:58px;font-weight:900;
  letter-spacing:-3px;margin-bottom:16px;
  position:relative;z-index:1;
}
.hero p{
  font-size:20px;opacity:.92;
  position:relative;z-index:1;font-weight:500;
}

/* ===================== BADGES ===================== */
.badge{
  display:inline-block;
  background:var(--purple);color:var(--white);
  font-size:11px;font-weight:700;
  padding:5px 12px;border-radius:20px;
  text-transform:uppercase;letter-spacing:.8px;
}
.badge-red{background:var(--red)}
.badge-black{background:var(--black)}

/* ===================== EMPTY ===================== */
.empty-state{
  text-align:center;padding:100px 20px;
  color:var(--gray-text);
  animation:fadeIn .5s ease;
}
.empty-state .icon{font-size:90px;margin-bottom:20px;opacity:.5}

/* ===================== ANIMATIONS ===================== */
@keyframes slideIn{
  from{opacity:0;transform:translateY(-12px)}
  to{opacity:1;transform:translateY(0)}
}
@keyframes fadeIn{
  from{opacity:0;transform:scale(.98)}
  to{opacity:1;transform:scale(1)}
}
@keyframes float{
  0%,100%{transform:translate(0,0) rotate(0)}
  50%{transform:translate(-24px,24px) rotate(8deg)}
}
@keyframes pulse{
  0%,100%{box-shadow:0 0 0 0 rgba(124,58,237,.7)}
  50%{box-shadow:0 0 0 12px rgba(124,58,237,0)}
}
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/shop" class="logo">MIDE<span class="logo-dot">.</span></a>
    <a href="/shop" class="nav-link">Catalog</a>
    {% if customer %}
    <a href="/shop/missions" class="nav-link">Missions</a>
    <a href="/shop/my-orders" class="nav-link">Orders</a>
    <a href="/shop/bonus" class="nav-link">Bonus</a>
    {% else %}
    <a href="/shop/login" class="nav-link">Login</a>
    <a href="/shop/register" class="nav-link">Register</a>
    {% endif %}
    <a href="/shop/cart" class="cart-btn">🛒 Cart</a>
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
    f.write(SHOP_BASE)
print("OK shop/base.html styled")

print()
print("Done! Now restart server.")