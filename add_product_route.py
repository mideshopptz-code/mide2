# -*- coding: utf-8 -*-
import re

content = open("web_app.py", encoding="utf-8").read()

if "def shop_product" in content:
    print("Route already exists")
    exit()

ROUTE = '''

@app.route("/shop/product/<int:pid>")
def shop_product(pid):
    """Красивая карточка товара для покупателя"""
    product = db.get_product(pid)
    if not product:
        flash("Товар не найден", "error")
        return redirect("/shop")

    seller = db.get_user_by_id(product["owner_id"])
    rating = db.get_seller_rating(product["owner_id"]) if seller else {"avg": 0, "count": 0}

    img = db.get_main_image(pid)
    if img:
        product["image"] = img.get("filename") if isinstance(img, dict) else img

    similar = []
    if product.get("category"):
        with db.connect() as conn:
            rows = conn.execute("""
                SELECT p.* FROM products p
                JOIN users u ON p.owner_id = u.id
                WHERE p.category = ? AND p.id != ? AND p.quantity > 0
                LIMIT 6
            """, (product["category"], pid)).fetchall()
            similar = [dict(r) for r in rows]
            for s in similar:
                si = db.get_main_image(s["id"])
                if si:
                    s["image"] = si.get("filename") if isinstance(si, dict) else si

    return render_template("shop/product_detail.html",
                            product=product,
                            seller=seller,
                            rating=rating,
                            similar=similar)

'''

marker = '@app.route("/shop/cart/add/'
if marker in content:
    content = content.replace(marker, ROUTE + "\n" + marker, 1)
    open("web_app.py", "w", encoding="utf-8").write(content)
    print("OK: route added")
else:
    print("ERROR: marker not found")

c = open("web_app.py", encoding="utf-8").read()
print()
print("Check:")
print("  shop_product:", "def shop_product" in c)
print("  /shop/product:", "/shop/product" in c)

import ast
try:
    ast.parse(c)
    print("SYNTAX OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e.lineno, e.msg)

print()
print("Done! Restart server.")