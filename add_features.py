# -*- coding: utf-8 -*- 
import os 
print("1. Migrating DB...") 
import sqlite3 
conn = sqlite3.connect("warehouse.db") 
c = conn.cursor() 
c.execute("CREATE TABLE IF NOT EXISTS promo_uses (id INTEGER PRIMARY KEY, code TEXT, customer_id INTEGER, order_id INTEGER, used_at TEXT)") 
conn.commit() 
conn.close() 
print("  DB OK") 
print("2. Updating database.py...") 
EXTRA = "\n    def dashboard_stats(self, days=30):\n        with self.connect() as conn:\n            r = conn.execute(\"SELECT COUNT(*) as total_orders, SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) as delivered, COALESCE(SUM(CASE WHEN status='delivered' THEN total_amount ELSE 0 END), 0) as revenue FROM orders\").fetchone()\n            return dict(r) if r else {}\n\n    def top_products(self, days=30, limit=10):\n        with self.connect() as conn:\n            rows = conn.execute(\"SELECT oi.product_name, SUM(oi.quantity) as qty, SUM(oi.subtotal) as revenue FROM order_items oi JOIN orders o ON oi.order_id = o.id WHERE o.status='delivered' GROUP BY oi.product_name ORDER BY revenue DESC LIMIT ?\", (limit,)).fetchall()\n            return [dict(r) for r in rows]\n\n    def top_sellers(self, days=30, limit=10):\n        with self.connect() as conn:\n            rows = conn.execute(\"SELECT u.username, u.full_name, COUNT(*) as count, COALESCE(SUM(o.total_amount), 0) as revenue FROM orders o JOIN users u ON o.taken_by = u.id WHERE o.status='delivered' GROUP BY u.id ORDER BY revenue DESC LIMIT ?\", (limit,)).fetchall()\n            return [dict(r) for r in rows]\n\n    def list_zones(self):\n        with self.connect() as conn:\n            return [dict(r) for r in conn.execute(\"SELECT * FROM delivery_zones ORDER BY name\").fetchall()]\n\n    def add_zone(self, name, fee, free_from=0, eta=60):\n        with self.connect() as conn:\n            c = conn.cursor()\n            c.execute(\"INSERT INTO delivery_zones (name, delivery_fee, free_from, eta_minutes, created_at) VALUES (?, ?, ?, ?, datetime('now'))\", (name, fee, free_from, eta))\n            return c.lastrowid\n\n    def list_missions(self):\n        with self.connect() as conn:\n            return [dict(r) for r in conn.execute(\"SELECT * FROM missions WHERE is_active=1 ORDER BY sort_order\").fetchall()]\n\n    def list_product_images(self, product_id):\n        with self.connect() as conn:\n            return [dict(r) for r in conn.execute(\"SELECT * FROM product_images WHERE product_id=? ORDER BY id\", (product_id,)).fetchall()]\n\n    def kpi_leaderboard(self, days=30):\n        with self.connect() as conn:\n            rows = conn.execute(\"SELECT u.id, u.username, u.full_name, u.role, COUNT(s.id) as sales_count, COALESCE(SUM(s.actual_amount), 0) as revenue FROM users u LEFT JOIN sales s ON s.seller_id = u.id AND s.status='approved' WHERE u.role IN ('seller','mentor') GROUP BY u.id ORDER BY revenue DESC\").fetchall()\n            result = []\n            for i, r in enumerate(rows, 1):\n                d = dict(r)\n                d['rank'] = i\n                d['accuracy'] = 100\n                result.append(d)\n            return result\n" 
content = open("database.py", encoding="utf-8").read() 
if "def dashboard_stats" not in content: 
    content += EXTRA 
    open("database.py", "w", encoding="utf-8").write(content) 
    print("  database.py updated") 
else: 
    print("  database.py already updated") 
print("DONE") 
