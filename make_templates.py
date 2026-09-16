# -*- coding: utf-8 -*-
import os

FILES = {}

FILES["templates/base.html"] = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{% block title %}Warehouse{% endblock %}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#f4f6f9;color:#333}
nav{background:#2c3e50;color:#fff;padding:12px 24px;display:flex;gap:12px;flex-wrap:wrap;align-items:center}
nav a{color:#ecf0f1;text-decoration:none;padding:6px 12px;border-radius:4px;font-size:14px}
nav a:hover{background:#34495e}
.container{max-width:1200px;margin:24px auto;padding:0 16px}
.card{background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,.08);margin-bottom:20px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:20px}
.stat-box{background:#fff;padding:16px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,.08)}
.stat-box h3{color:#7f8c8d;font-size:13px;text-transform:uppercase;margin-bottom:6px}
.stat-box .value{font-size:26px;font-weight:bold;color:#2c3e50}
table{width:100%;border-collapse:collapse}
th,td{padding:10px;text-align:left;border-bottom:1px solid #ecf0f1}
th{background:#34495e;color:#fff}
.btn{display:inline-block;padding:8px 14px;background:#3498db;color:#fff;border:none;border-radius:4px;cursor:pointer;text-decoration:none;font-size:14px}
.btn-success{background:#27ae60}.btn-danger{background:#e74c3c}.btn-warning{background:#f39c12}
.btn-sm{padding:4px 10px;font-size:12px}
input,select,textarea{padding:8px 12px;border:1px solid #ddd;border-radius:4px;width:100%;margin-bottom:12px;font-size:14px}
label{display:block;margin-bottom:4px;font-weight:600;color:#555;font-size:13px}
.flash{padding:12px;border-radius:4px;margin-bottom:16px}
.flash.success{background:#d4edda;color:#155724}
.flash.error{background:#f8d7da;color:#721c24}
h1{margin-bottom:16px;color:#2c3e50}
#toast{position:fixed;top:20px;right:20px;z-index:9999}
.toast{background:#2c3e50;color:#fff;padding:14px 18px;border-radius:8px;margin-bottom:10px;box-shadow:0 4px 12px rgba(0,0,0,.2);cursor:pointer;min-width:260px}
.role-badge{padding:2px 8px;border-radius:10px;font-size:11px;color:#fff;font-weight:bold}
.role-admin{background:#e74c3c}
.role-senior_seller{background:#f39c12}
.role-mentor{background:#3498db}
.role-seller{background:#95a5a6}
</style></head><body>
<nav>
<strong>Warehouse</strong>
{% if user %}
<a href="/">Products</a>
<a href="/sales">Sales</a>
<a href="/orders">Orders</a>
<a href="/defects">Defects</a>
<a href="/transfers">Transfers</a>
{% if user.role in ('admin','senior_seller','mentor') %}
<a href="/team">Team</a>
<a href="/revisions">Revisions</a>
{% endif %}
{% if user.role == 'admin' %}
<a href="/staff">Employees</a>
{% endif %}
<a href="/profile">Profile</a>
<a href="/notifications">Notifications</a>
<span style="margin-left:auto;font-size:13px">
{{ user.full_name or user.username }}
<span class="role-badge role-{{ user.role }}">{{ user.role }}</span>
</span>
<a href="/logout">Logout</a>
{% endif %}
</nav>
<div class="container">
{% with messages = get_flashed_messages(with_categories=true) %}
{% for cat,msg in messages %}<div class="flash {{cat}}">{{msg}}</div>{% endfor %}
{% endwith %}
{% block content %}{% endblock %}
</div>
<div id="toast"></div>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<script>
var socket = io();
socket.on('staff_notification', function(d){ showToast(d.title, d.body); });
function showToast(title, body){
    var box = document.getElementById('toast');
    var el = document.createElement('div');
    el.className = 'toast';
    el.innerHTML = '<b>'+title+'</b><br><span style="font-size:13px">'+(body||'')+'</span>';
    el.onclick = function(){ el.remove(); };
    box.appendChild(el);
    setTimeout(function(){ el.remove(); }, 8000);
}
</script>
{% block scripts %}{% endblock %}
</body></html>"""

FILES["templates/staff_form.html"] = """{% extends "base.html" %}{% block content %}
<div class="card" style="max-width:600px;margin:auto">
<h1>{{ 'Edit' if user else 'Add' }} employee</h1>
<form method="post">
    <label>Username</label>
    <input name="username" value="{{ user.username if user else '' }}"
           {% if user %}disabled{% else %}required{% endif %}>
    <label>Password {% if user %}(leave empty to keep){% endif %}</label>
    <input name="password" type="password" {% if not user %}required{% endif %}>
    <label>Full name</label>
    <input name="full_name" value="{{ user.full_name if user else '' }}">
    <label>Role</label>
    <select name="role" {% if user and user.role == 'admin' %}disabled{% endif %}>
        <option value="senior_seller" {% if user and user.role == 'senior_seller' %}selected{% endif %}>Senior Seller</option>
        <option value="mentor" {% if user and user.role == 'mentor' %}selected{% endif %}>Mentor</option>
        <option value="seller" {% if user and user.role == 'seller' %}selected{% endif %}>Seller</option>
    </select>
    <label>Manager (who reports to this person)</label>
    <select name="parent_id">
        <option value="">-- none --</option>
        {% for p in parents %}
        <option value="{{ p.id }}"
            {% if user and user.parent_id == p.id %}selected{% endif %}>
            {{ p.full_name or p.username }} ({{ p.role }})
        </option>
        {% endfor %}
    </select>
    <label>Commission rate (%)</label>
    <input name="commission_rate" type="number" step="0.1" min="0" max="100"
           value="{{ user.commission_rate if user else 0 }}">
    <button class="btn btn-success" type="submit">Save</button>
    <a href="/staff" class="btn" style="background:#95a5a6">Cancel</a>
</form>
</div>
{% endblock %}"""

FILES["templates/profile.html"] = """{% extends "base.html" %}{% block content %}
<h1>My Profile</h1>

<div class="card" style="max-width:600px">
    <h3>Info</h3>
    <p><b>Username:</b> {{ profile_user.username }}</p>
    <p><b>Role:</b> <span class="role-badge role-{{ profile_user.role }}">{{ profile_user.role }}</span></p>
    <p><b>Commission:</b> {{ profile_user.commission_rate or 0 }}%</p>
</div>

<div class="card" style="max-width:600px">
    <h3>Telegram notifications</h3>
    {% if profile_user.telegram_id %}
        <p>Telegram linked (ID: {{ profile_user.telegram_id }})</p>
        <form method="post">
            <button class="btn btn-danger" name="unlink_telegram" type="submit">Unlink</button>
        </form>
    {% else %}
        <p>Not linked yet. Get a code and send it to the bot.</p>
        {% if profile_user.telegram_code %}
        <div style="background:#fff3cd;padding:12px;border-radius:6px;margin-bottom:12px">
            <b>Your code:</b> <code>{{ profile_user.telegram_code }}</code><br>
            Send to bot: <code>/link {{ profile_user.telegram_code }}</code>
        </div>
        {% endif %}
        <form method="post">
            <button class="btn btn-success" name="generate_code" type="submit">Get code</button>
        </form>
    {% endif %}
</div>

<div class="card" style="max-width:600px">
    <h3>Edit name</h3>
    <form method="post">
        <label>Full name</label>
        <input name="full_name" value="{{ profile_user.full_name or '' }}">
        <button class="btn btn-success" name="save" type="submit">Save</button>
    </form>
</div>
{% endblock %}"""

FILES["templates/team.html"] = """{% extends "base.html" %}{% block content %}
<h1>My Team</h1>
<div class="card">
    <a href="/revisions/new" class="btn btn-warning">+ Request revision</a>
</div>
<div class="card">
<table>
<thead><tr>
    <th>ID</th><th>Name</th><th>Role</th>
    <th>Products</th><th>Stock value</th><th></th>
</tr></thead>
<tbody>
{% for m in team %}
<tr>
    <td>{{ m.user.id }}</td>
    <td>{{ m.user.full_name or m.user.username }}</td>
    <td><span class="role-badge role-{{ m.user.role }}">{{ m.user.role }}</span></td>
    <td>{{ m.products_count }}</td>
    <td>{{ '%.2f'|format(m.total_value) }} RUB</td>
    <td><a href="/team/member/{{ m.user.id }}" class="btn btn-sm">View</a></td>
</tr>
{% else %}
<tr><td colspan="6" style="text-align:center;padding:20px">No subordinates yet</td></tr>
{% endfor %}
</tbody></table>
</div>
{% endblock %}"""

FILES["templates/team_member.html"] = """{% extends "base.html" %}{% block content %}
<h1>{{ member.full_name or member.username }}'s warehouse</h1>
<div class="card">
    <p><b>Role:</b> <span class="role-badge role-{{ member.role }}">{{ member.role }}</span></p>
    <p><b>Total value:</b> {{ '%.2f'|format(total_value) }} RUB</p>
</div>
<div class="card">
<table>
<thead><tr><th>Name</th><th>Category</th><th>Qty</th><th>Price</th></tr></thead>
<tbody>
{% for p in products %}
<tr>
    <td>{{ p.name }}</td>
    <td>{{ p.category or '-' }}</td>
    <td>{{ p.quantity }}</td>
    <td>{{ '%.2f'|format(p.price) }} RUB</td>
</tr>
{% else %}
<tr><td colspan="4" style="text-align:center;padding:20px">No products</td></tr>
{% endfor %}
</tbody></table>
</div>
{% endblock %}"""

FILES["templates/sales.html"] = """{% extends "base.html" %}{% block content %}
<h1>Sales</h1>
<div class="card">
    <a href="/sales/new" class="btn btn-success">+ New sale</a>
</div>
<div class="card">
<table>
<thead><tr>
    <th>ID</th><th>Seller</th><th>Product</th><th>Qty</th>
    <th>Expected</th><th>Actual</th><th>Status</th><th></th>
</tr></thead>
<tbody>
{% for s in sales %}
<tr {% if not s.is_correct %}style="background:#fff5f5"{% endif %}>
    <td>{{ s.id }}</td>
    <td>{{ s.seller_name or s.seller_username }}</td>
    <td>{{ s.product_name }}</td>
    <td>{{ s.quantity }}</td>
    <td>{{ '%.2f'|format(s.expected_amount) }} RUB</td>
    <td style="color:{% if s.is_correct %}#27ae60{% else %}#e74c3c{% endif %}">
        <b>{{ '%.2f'|format(s.actual_amount) }} RUB</b>
        {% if not s.is_correct %} !!{% endif %}
    </td>
    <td>
        {% if s.status == 'pending' %}pending
        {% elif s.status == 'approved' %}approved
        {% else %}rejected{% endif %}
    </td>
    <td>
        {% if s.status == 'pending' and user.role in ('admin','senior_seller','mentor') and user.id != s.seller_id %}
        <form method="post" action="/sales/{{ s.id }}/approve" style="display:inline">
            <button class="btn btn-sm btn-success">OK</button>
        </form>
        <form method="post" action="/sales/{{ s.id }}/reject" style="display:inline">
            <button class="btn btn-sm btn-danger">NO</button>
        </form>
        {% endif %}
    </td>
</tr>
{% else %}
<tr><td colspan="8" style="text-align:center;padding:20px">No sales</td></tr>
{% endfor %}
</tbody></table>
</div>
{% endblock %}"""

FILES["templates/sale_new.html"] = """{% extends "base.html" %}{% block content %}
<div class="card" style="max-width:600px;margin:auto">
<h1>New sale</h1>
<p style="color:#7f8c8d">Your commission: <b>{{ user.commission_rate or 0 }}%</b></p>

<form method="post" id="saleForm">
    <label>Product</label>
    <select name="product_id" id="productSelect" required>
        <option value="">-- choose --</option>
        {% for p in products %}
        <option value="{{ p.id }}" data-price="{{ p.price }}" data-qty="{{ p.quantity }}">
            {{ p.name }} ({{ p.quantity }} pcs, {{ '%.2f'|format(p.price) }} RUB)
        </option>
        {% endfor %}
    </select>

    <label>Quantity</label>
    <input type="number" name="quantity" id="qtyInput" min="1" required>

    <div style="background:#f8f9fa;padding:12px;border-radius:6px;margin-bottom:12px">
        <div>Gross: <b id="grossSum">0.00</b> RUB</div>
        <div>Commission: <b id="commSum">0.00</b> RUB</div>
        <div style="font-size:16px;margin-top:4px">
            Expected: <b id="expectedSum" style="color:#27ae60">0.00</b> RUB
        </div>
    </div>

    <label>Actual amount received</label>
    <input type="number" step="0.01" name="actual_amount" id="actualInput" required>

    <div id="warnBox" style="display:none;padding:10px;border-radius:4px;background:#f8d7da;color:#721c24;font-weight:bold;margin-bottom:12px">
        WARNING! Expected <span id="expectedShow"></span> RUB, diff: <span id="diffShow"></span> RUB
    </div>

    <label>Comment</label>
    <textarea name="comment" rows="2"></textarea>
    <button class="btn btn-success" type="submit">Send for approval</button>
</form>
</div>

<script>
var RATE = {{ user.commission_rate or 0 }};
var ps = document.getElementById('productSelect');
var qty = document.getElementById('qtyInput');
var act = document.getElementById('actualInput');
var gs = document.getElementById('grossSum');
var cs = document.getElementById('commSum');
var es = document.getElementById('expectedSum');
var wb = document.getElementById('warnBox');

function recalc(){
    var opt = ps.selectedOptions[0];
    if(!opt || !opt.value){ gs.textContent='0.00'; cs.textContent='0.00'; es.textContent='0.00'; return 0; }
    var price = parseFloat(opt.dataset.price) || 0;
    var q = parseInt(qty.value) || 0;
    var gross = price * q;
    var comm = gross * (RATE / 100);
    var expected = gross - comm;
    gs.textContent = gross.toFixed(2);
    cs.textContent = comm.toFixed(2);
    es.textContent = expected.toFixed(2);
    var a = parseFloat(act.value) || 0;
    if(act.value !== '' && Math.abs(a - expected) >= 0.01){
        wb.style.display='block';
        document.getElementById('expectedShow').textContent = expected.toFixed(2);
        document.getElementById('diffShow').textContent = (a - expected).toFixed(2);
    } else { wb.style.display='none'; }
    return expected;
}
ps.addEventListener('change', function(){
    var opt = ps.selectedOptions[0];
    if(opt && opt.value){ qty.max = opt.dataset.qty; qty.value = 1; }
    recalc();
});
qty.addEventListener('input', recalc);
act.addEventListener('input', recalc);
</script>
{% endblock %}"""

FILES["templates/defects.html"] = """{% extends "base.html" %}{% block content %}
<h1>Defect requests</h1>
<div class="card">
    <a href="/defects/new" class="btn btn-danger">+ New defect</a>
</div>
<div class="card">
<table>
<thead><tr>
    <th>ID</th><th>Seller</th><th>Product</th><th>Qty</th>
    <th>Reason</th><th>Status</th><th></th>
</tr></thead>
<tbody>
{% for d in defects %}
<tr>
    <td>{{ d.id }}</td>
    <td>{{ d.seller_name or d.seller_username }}</td>
    <td>{{ d.product_name }}</td>
    <td>{{ d.quantity }}</td>
    <td style="font-size:12px">{{ d.reason or '-' }}</td>
    <td>{{ d.status }}</td>
    <td>
        {% if d.status == 'pending' and user.role in ('admin','senior_seller','mentor') and user.id != d.seller_id %}
        <form method="post" action="/defects/{{ d.id }}/approve" style="display:inline">
            <button class="btn btn-sm btn-success">OK</button>
        </form>
        <form method="post" action="/defects/{{ d.id }}/reject" style="display:inline">
            <button class="btn btn-sm btn-danger">NO</button>
        </form>
        {% endif %}
    </td>
</tr>
{% else %}
<tr><td colspan="7" style="text-align:center;padding:20px">No defects</td></tr>
{% endfor %}
</tbody></table>
</div>
{% endblock %}"""

FILES["templates/defect_new.html"] = """{% extends "base.html" %}{% block content %}
<div class="card" style="max-width:500px;margin:auto">
<h1>New defect request</h1>
<form method="post">
    <label>Product</label>
    <select name="product_id" required>
        <option value="">-- choose --</option>
        {% for p in products %}
        <option value="{{ p.id }}">{{ p.name }} ({{ p.quantity }} pcs)</option>
        {% endfor %}
    </select>
    <label>Quantity</label>
    <input name="quantity" type="number" min="1" required>
    <label>Reason</label>
    <textarea name="reason" rows="3" placeholder="What happened?"></textarea>
    <button class="btn btn-danger" type="submit">Send request</button>
</form>
</div>
{% endblock %}"""

FILES["templates/transfers.html"] = """{% extends "base.html" %}{% block content %}
<h1>Transfers</h1>
<div class="card">
    <a href="/transfers/new" class="btn btn-success">+ New transfer</a>
</div>
<div class="card">
<table>
<thead><tr>
    <th>ID</th><th>From</th><th>To</th><th>Product</th><th>Qty</th>
    <th>Status</th><th>Admin?</th><th></th>
</tr></thead>
<tbody>
{% for t in transfers %}
<tr>
    <td>{{ t.id }}</td>
    <td>{{ t.from_name or t.from_username }}</td>
    <td>{{ t.to_name or t.to_username }}</td>
    <td>{{ t.product_name }}</td>
    <td>{{ t.quantity }}</td>
    <td>{{ t.status }}</td>
    <td>{% if t.requires_admin %}yes{% endif %}</td>
    <td>
        {% if t.status == 'pending' and user.role in ('admin','senior_seller') %}
        <form method="post" action="/transfers/{{ t.id }}/approve" style="display:inline">
            <button class="btn btn-sm btn-success">OK</button>
        </form>
        <form method="post" action="/transfers/{{ t.id }}/reject" style="display:inline">
            <button class="btn btn-sm btn-danger">NO</button>
        </form>
        {% endif %}
    </td>
</tr>
{% else %}
<tr><td colspan="8" style="text-align:center;padding:20px">No transfers</td></tr>
{% endfor %}
</tbody></table>
</div>
{% endblock %}"""

FILES["templates/transfer_new.html"] = """{% extends "base.html" %}{% block content %}
<div class="card" style="max-width:500px;margin:auto">
<h1>New transfer</h1>
{% if user.role == 'senior_seller' %}
<div style="background:#fff3cd;padding:10px;border-radius:4px;margin-bottom:12px">
    Senior transfers require admin approval
</div>
{% endif %}
<form method="post">
    <label>To employee</label>
    <select name="to_user_id" required>
        <option value="">-- choose --</option>
        {% for u in users %}
        <option value="{{ u.id }}">{{ u.full_name or u.username }} ({{ u.role }})</option>
        {% endfor %}
    </select>
    <label>Product</label>
    <select name="product_id" required>
        <option value="">-- choose --</option>
        {% for p in products %}
        <option value="{{ p.id }}">{{ p.name }} ({{ p.quantity }} pcs)</option>
        {% endfor %}
    </select>
    <label>Quantity</label>
    <input name="quantity" type="number" min="1" required>
    <label>Comment</label>
    <textarea name="comment" rows="2"></textarea>
    <button class="btn btn-success" type="submit">Create transfer</button>
</form>
</div>
{% endblock %}"""

FILES["templates/revisions.html"] = """{% extends "base.html" %}{% block content %}
<h1>Revisions</h1>
<div class="card">
    <a href="/revisions/new" class="btn btn-warning">+ Request revision</a>
</div>
<div class="card">
<table>
<thead><tr>
    <th>ID</th><th>Requester</th><th>Target</th>
    <th>Status</th><th>Created</th><th></th>
</tr></thead>
<tbody>
{% for r in revisions %}
<tr>
    <td>{{ r.id }}</td>
    <td>{{ r.requester_name }}</td>
    <td>{{ r.target_name or r.target_username }}</td>
    <td>{{ r.status }}</td>
    <td style="font-size:12px">{{ r.created_at }}</td>
    <td><a href="/revisions/{{ r.id }}" class="btn btn-sm">Open</a></td>
</tr>
{% else %}
<tr><td colspan="6" style="text-align:center;padding:20px">No revisions</td></tr>
{% endfor %}
</tbody></table>
</div>
{% endblock %}"""

FILES["templates/revision_new.html"] = """{% extends "base.html" %}{% block content %}
<div class="card" style="max-width:500px;margin:auto">
<h1>Request revision</h1>
<form method="post">
    <label>Who to check</label>
    <select name="target_user_id" required>
        <option value="">-- choose --</option>
        {% for t in targets %}
        <option value="{{ t.id }}">{{ t.full_name or t.username }} ({{ t.role }})</option>
        {% endfor %}
    </select>
    <label>Comment</label>
    <textarea name="comment" rows="2"></textarea>
    <button class="btn btn-warning" type="submit">Request</button>
</form>
</div>
{% endblock %}"""

FILES["templates/revision_detail.html"] = """{% extends "base.html" %}{% block content %}
<h1>Revision #{{ revision.id }}</h1>

<div class="card">
    <p><b>Target:</b> {{ target.full_name or target.username }}</p>
    <p><b>Status:</b> {{ revision.status }}</p>
    {% if revision.comment %}<p><b>Comment:</b> {{ revision.comment }}</p>{% endif %}
</div>

{% if revision.status == 'requested' %}
<form method="post">
    <div class="card">
        <h3>Enter actual quantities</h3>
        <table>
            <thead><tr><th>Product</th><th>Expected</th><th>Actual</th></tr></thead>
            <tbody>
            {% for p in products %}
            <tr>
                <td>{{ p.name }}</td>
                <td>{{ p.quantity }}</td>
                <td><input type="number" name="actual_{{ p.id }}"
                           value="{{ p.quantity }}" min="0"
                           style="width:100px;margin:0"></td>
            </tr>
            {% endfor %}
            </tbody>
        </table>
        <br>
        <label>Result comment</label>
        <textarea name="comment" rows="2"></textarea>
        <br>
        <button class="btn btn-success" type="submit">Complete revision</button>
    </div>
</form>
{% endif %}

{% if items %}
<div class="card">
    <h3>Results</h3>
    <table>
        <thead><tr><th>Product</th><th>Expected</th><th>Actual</th><th>Diff</th></tr></thead>
        <tbody>
        {% for i in items %}
        <tr>
            <td>{{ i.product_name }}</td>
            <td>{{ i.expected_qty }}</td>
            <td>{{ i.actual_qty }}</td>
            <td style="font-weight:bold">
                {% if i.diff > 0 %}+{% endif %}{{ i.diff }}</td>
        </tr>
        {% endfor %}
        </tbody>
    </table>
</div>
{% endif %}
{% endblock %}"""

FILES["templates/shop/base.html"] = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{% block title %}Shop{% endblock %}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#f5f6f8;color:#333}
nav{background:#e74c3c;color:#fff;padding:14px 20px;display:flex;gap:16px;flex-wrap:wrap;align-items:center}
nav a{color:#fff;text-decoration:none;padding:6px 12px;border-radius:4px}
nav a:hover{background:rgba(255,255,255,.15)}
.container{max-width:1100px;margin:20px auto;padding:0 16px}
.card{background:#fff;padding:20px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);margin-bottom:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}
.product{background:#fff;border-radius:10px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.product h3{font-size:15px;margin-bottom:6px}
.product .price{font-size:18px;font-weight:bold;color:#e74c3c;margin:8px 0}
.btn{display:inline-block;padding:8px 16px;background:#e74c3c;color:#fff;border:none;border-radius:6px;cursor:pointer;text-decoration:none;font-size:14px}
.btn-success{background:#27ae60}
.btn-sm{padding:5px 10px;font-size:13px}
input,textarea,select{padding:10px 14px;border:1px solid #ddd;border-radius:6px;width:100%;margin-bottom:12px;font-size:15px}
label{display:block;margin-bottom:4px;font-weight:600;color:#555;font-size:13px}
.flash{padding:12px;border-radius:6px;margin-bottom:16px}
.flash.success{background:#d4edda;color:#155724}
.flash.error{background:#f8d7da;color:#721c24}
h1{margin-bottom:16px;color:#2c3e50}
</style></head><body>
<nav>
<a href="/shop" style="font-weight:bold">Shop</a>
{% if customer %}
<a href="/shop/my-orders">My orders</a>
<a href="/shop/bonus">Bonus ({{ customer.bonus_points or 0 }})</a>
<a href="/shop/cart">Cart</a>
<span style="margin-left:auto">Hi, {{ customer.name }}</span>
<a href="/shop/logout">Logout</a>
{% else %}
<a href="/shop/login">Login</a>
<a href="/shop/register">Register</a>
<a href="/shop/cart">Cart</a>
{% endif %}
</nav>
<div class="container">
{% with messages = get_flashed_messages(with_categories=true) %}
{% for cat,msg in messages %}<div class="flash {{cat}}">{{msg}}</div>{% endfor %}
{% endwith %}
{% block content %}{% endblock %}
</div>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<script>
var socket = io();
socket.on('customer_notification', function(d){
    alert(d.title + '\\n' + (d.body || ''));
});
</script>
</body></html>"""

FILES["templates/shop/bonus.html"] = """{% extends "shop/base.html" %}{% block content %}
<h1>My bonus points</h1>
<div class="card" style="background:linear-gradient(135deg,#f39c12,#e74c3c);color:#fff">
    <h3 style="color:#fff">Balance</h3>
    <div style="font-size:48px;font-weight:bold">{{ customer.bonus_points or 0 }}</div>
    <div style="opacity:.9">1 point = 1 RUB discount</div>
</div>
<div class="card">
    <p><b>How it works:</b></p>
    <ul style="margin-left:20px;margin-top:10px">
        <li>Get 1% back from each delivered order</li>
        <li>Spend points at checkout</li>
        <li>Minimum 100 points to spend</li>
    </ul>
</div>
{% endblock %}"""

FILES["templates/shop/cart.html"] = """{% extends "shop/base.html" %}{% block content %}
<h1>Cart</h1>
{% if items %}
<div class="card">
<table>
<thead><tr><th>Product</th><th>Price</th><th>Qty</th><th>Subtotal</th></tr></thead>
<tbody>
{% for it in items %}
<tr><td>{{ it.product.name }}</td><td>{{ '%.2f'|format(it.product.price) }} RUB</td>
<td>{{ it.quantity }}</td><td>{{ '%.2f'|format(it.subtotal) }} RUB</td></tr>
{% endfor %}
</tbody></table>
<div style="text-align:right;margin-top:16px;font-size:20px">
Total: <b style="color:#e74c3c">{{ '%.2f'|format(total) }} RUB</b>
</div>
</div>

{% if customer %}
<div class="card">
<h3>Checkout</h3>
<form method="post" action="/shop/checkout">
    <label>Delivery address *</label>
    <input name="address" required value="{{ customer.district or '' }}">

    {% if customer.bonus_points and customer.bonus_points >= 100 %}
    <div style="background:#fff3cd;padding:12px;border-radius:6px;margin-bottom:12px">
        <b>You have {{ customer.bonus_points }} points!</b>
        <label style="margin-top:8px">Spend points (max 50% of order)</label>
        <input name="bonus_spent" type="number" min="0"
               max="{{ customer.bonus_points }}"
               value="0" style="margin:0">
    </div>
    {% endif %}

    <label>Comment</label>
    <textarea name="comment" rows="2"></textarea>
    <button class="btn" type="submit" style="width:100%;padding:14px">Place order</button>
</form>
</div>
{% else %}
<div class="card" style="text-align:center;padding:30px">
<p style="margin-bottom:16px">Login to place an order</p>
<a href="/shop/login" class="btn">Login</a>
</div>
{% endif %}

{% else %}
<div class="card" style="text-align:center;padding:60px">
<p style="font-size:18px;color:#7f8c8d;margin-bottom:20px">Cart is empty</p>
<a href="/shop" class="btn">Go to catalog</a>
</div>
{% endif %}
{% endblock %}"""

# Создаём
print("Creating files...")
for path, content in FILES.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  OK " + path)

print()
print("All files created!")