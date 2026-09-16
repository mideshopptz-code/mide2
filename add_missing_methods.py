# -*- coding: utf-8 -*-

content = open("database.py", encoding="utf-8").read()

# Проверяем
methods = [
    ("get_main_image", "def get_main_image"),
    ("get_seller_rating", "def get_seller_rating"),
    ("get_product_images", "def get_product_images"),
    ("add_product_image", "def add_product_image"),
]

print("До:")
for name, marker in methods:
    print("  " + name + ":", marker in content)
print()

EXTRA = '''

    # ================= PRODUCT IMAGES =================
    def get_main_image(self, product_id):
        with self.connect() as conn:
            r = conn.execute("""SELECT filename FROM product_images
                                WHERE product_id = ?
                                ORDER BY is_main DESC, id ASC LIMIT 1""",
                             (product_id,)).fetchone()
            if r:
                return {"filename": r["filename"]}
            return None

    def get_product_images(self, product_id):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("""
                SELECT * FROM product_images WHERE product_id = ?
                ORDER BY is_main DESC, id ASC
            """, (product_id,)).fetchall()]

    def add_product_image(self, product_id, filename, thumb_filename="", is_main=0):
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO product_images
                (product_id, filename, thumb_filename, is_main, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (product_id, filename, thumb_filename, is_main, now))
            return c.lastrowid

    # ================= REVIEWS =================
    def get_seller_rating(self, seller_id):
        with self.connect() as conn:
            r = conn.execute("""SELECT AVG(rating) as avg_rating, COUNT(*) as count
                                FROM seller_reviews
                                WHERE seller_id = ? AND is_published = 1""",
                             (seller_id,)).fetchone()
            if not r:
                return {"avg": 0, "count": 0}
            return {
                "avg": round(r["avg_rating"] or 0, 2),
                "count": r["count"] or 0,
            }

    def get_reviews_for_seller(self, seller_id, limit=20):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("""
                SELECT r.*, c.name as customer_name
                FROM seller_reviews r
                JOIN customers c ON r.customer_id = c.id
                WHERE r.seller_id = ? AND r.is_published = 1
                ORDER BY r.created_at DESC LIMIT ?
            """, (seller_id, limit)).fetchall()]
'''

missing = [name for name, marker in methods if marker not in content]

if missing:
    print("Добавляем:", ", ".join(missing))
    if not content.endswith("\n"):
        content += "\n"
    content += EXTRA
    open("database.py", "w", encoding="utf-8").write(content)
    print("OK: методы добавлены")
else:
    print("Все методы уже есть")

c = open("database.py", encoding="utf-8").read()
print()
print("После:")
for name, marker in methods:
    print("  " + name + ":", marker in c)

import ast
try:
    ast.parse(c)
    print()
    print("SYNTAX OK!")
except SyntaxError as e:
    print()
    print("SYNTAX ERROR:", e.lineno, e.msg)

print()
print("Done! Restart server.")