import sqlite3
from datetime import datetime
from contextlib import contextmanager
from config import Config


class WarehouseDB:
    def __init__(self, db_name=None):
        self.db_name = db_name or Config.DB_NAME
        self.create_tables()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def create_tables(self):
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT NOT NULL DEFAULT 'seller',
                parent_id INTEGER,
                commission_rate REAL DEFAULT 0.0,
                telegram_id INTEGER,
                telegram_code TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT)""")

            c.execute("""CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER DEFAULT 0,
                price REAL DEFAULT 0.0,
                min_stock INTEGER DEFAULT 5,
                created_at TEXT,
                updated_at TEXT)""")

            c.execute("""CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                district TEXT,
                bonus_points INTEGER DEFAULT 0,
                created_at TEXT)""")

            c.execute("""CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                address TEXT,
                total_amount REAL DEFAULT 0.0,
                bonus_spent INTEGER DEFAULT 0,
                status TEXT DEFAULT 'new',
                comment TEXT,
                taken_by INTEGER,
                created_at TEXT)""")

            c.execute("""CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                product_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                subtotal REAL NOT NULL)""")

            c.execute("""CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                sender_type TEXT NOT NULL,
                sender_name TEXT,
                message TEXT,
                created_at TEXT)""")

            c.execute("""CREATE TABLE IF NOT EXISTS user_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT,
                body TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TEXT)""")

            c.execute("""CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT,
                quantity INTEGER NOT NULL,
                base_price REAL NOT NULL,
                commission_rate REAL NOT NULL,
                expected_amount REAL NOT NULL,
                actual_amount REAL NOT NULL,
                is_correct INTEGER DEFAULT 0,
                comment TEXT,
                status TEXT DEFAULT 'pending',
                reviewed_by INTEGER,
                created_at TEXT)""")

            c.execute("""CREATE TABLE IF NOT EXISTS defects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT,
                quantity INTEGER NOT NULL,
                reason TEXT,
                status TEXT DEFAULT 'pending',
                reviewed_by INTEGER,
                review_comment TEXT,
                created_at TEXT)""")

            c.execute("""CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT,
                quantity INTEGER NOT NULL,
                comment TEXT,
                status TEXT DEFAULT 'pending',
                initiated_by INTEGER NOT NULL,
                requires_admin INTEGER DEFAULT 0,
                approved_by INTEGER,
                created_at TEXT)""")

            c.execute("""CREATE TABLE IF NOT EXISTS revisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requester_id INTEGER NOT NULL,
                target_user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'requested',
                comment TEXT,
                result_comment TEXT,
                created_at TEXT,
                completed_at TEXT)""")

            c.execute("""CREATE TABLE IF NOT EXISTS revision_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                revision_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT,
                expected_qty INTEGER,
                actual_qty INTEGER,
                diff INTEGER)""")

            c.execute("SELECT COUNT(*) FROM users")
            if c.fetchone()[0] == 0:
                from auth import hash_password
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("""INSERT INTO users
                    (username, password_hash, full_name, role, created_at)
                    VALUES (?, ?, ?, ?, ?)""",
                    ("admin", hash_password("admin123"), "Admin",
                     "admin", now))

        self._migrate()

    def _migrate(self):
        with self.connect() as conn:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
            for col, ddl in [
                ("parent_id", "INTEGER"),
                ("commission_rate", "REAL DEFAULT 0.0"),
                ("telegram_id", "INTEGER"),
                ("telegram_code", "TEXT"),
                ("is_active", "INTEGER DEFAULT 1"),
            ]:
                if col not in cols:
                    try:
                        conn.execute("ALTER TABLE users ADD COLUMN " + col + " " + ddl)
                    except Exception:
                        pass

            cols = [r[1] for r in conn.execute("PRAGMA table_info(customers)").fetchall()]
            if "bonus_points" not in cols:
                try:
                    conn.execute("ALTER TABLE customers ADD COLUMN bonus_points INTEGER DEFAULT 0")
                except Exception:
                    pass

            cols = [r[1] for r in conn.execute("PRAGMA table_info(orders)").fetchall()]
            if "bonus_spent" not in cols:
                try:
                    conn.execute("ALTER TABLE orders ADD COLUMN bonus_spent INTEGER DEFAULT 0")
                except Exception:
                    pass

    # ================= USERS =================
    def get_user(self, username):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM users WHERE username = ?",
                             (username,)).fetchone()
            return dict(r) if r else None

    def get_user_by_id(self, uid):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
            return dict(r) if r else None

    def create_user(self, username, password_hash, full_name="",
                    role="seller", parent_id=None, commission_rate=0.0):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO users
                (username, password_hash, full_name, role, parent_id,
                 commission_rate, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (username, password_hash, full_name, role, parent_id,
                 commission_rate, now))
            return c.lastrowid

    def list_users(self, role=None, parent_id=None):
        q = "SELECT * FROM users WHERE 1=1"
        params = []
        if role:
            q += " AND role = ?"
            params.append(role)
        if parent_id is not None:
            q += " AND parent_id = ?"
            params.append(parent_id)
        q += " ORDER BY id"
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def update_user(self, uid, **kwargs):
        allowed = ["full_name", "role", "password_hash", "parent_id",
                   "commission_rate", "telegram_id", "telegram_code", "is_active"]
        fields, values = [], []
        for k, v in kwargs.items():
            if k in allowed:
                fields.append(k + " = ?")
                values.append(v)
        if not fields:
            return False
        values.append(uid)
        with self.connect() as conn:
            conn.execute("UPDATE users SET " + ", ".join(fields) +
                         " WHERE id = ?", values)
        return True

    def delete_user(self, uid):
        with self.connect() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (uid,))

    def subordinates(self, uid):
        """Возвращает список ID всех подчинённых (прямых и косвенных)"""
        result = []
        queue = [uid]
        while queue:
            current = queue.pop(0)
            with self.connect() as conn:
                children = [r["id"] for r in conn.execute(
                    "SELECT id FROM users WHERE parent_id = ?", (current,)).fetchall()]
            for cid in children:
                if cid not in result:
                    result.append(cid)
                    queue.append(cid)
        return result

    def visible_user_ids(self, user):
        """Кто виден пользователю: он сам + подчинённые (для admin — все)"""
        if not user:
            return []
        if user["role"] == "admin":
            with self.connect() as conn:
                return [r["id"] for r in conn.execute(
                    "SELECT id FROM users").fetchall()]
        return [user["id"]] + self.subordinates(user["id"])

    # ================= TELEGRAM =================
    def get_user_by_telegram(self, telegram_id):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM users WHERE telegram_id = ?",
                             (telegram_id,)).fetchone()
            return dict(r) if r else None

    def get_user_by_telegram_code(self, code):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM users WHERE telegram_code = ?",
                             (code,)).fetchone()
            return dict(r) if r else None

    # ================= PRODUCTS =================
    def add_product(self, owner_id, name, category, quantity, price, min_stock=5):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO products
                (owner_id, name, category, quantity, price, min_stock,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (owner_id, name, category, quantity, price, min_stock, now, now))
            return c.lastrowid

    def get_products(self, owner_id):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM products WHERE owner_id = ? ORDER BY id",
                (owner_id,)).fetchall()]

    def get_all_products(self):
        with self.connect() as conn:
            rows = conn.execute("""SELECT p.*, u.full_name as seller_name,
                                          u.username as seller_username
                                   FROM products p
                                   JOIN users u ON p.owner_id = u.id
                                   WHERE p.quantity > 0
                                   ORDER BY p.name""").fetchall()
            return [dict(r) for r in rows]

    def get_product(self, pid, owner_id=None):
        with self.connect() as conn:
            if owner_id:
                r = conn.execute("""SELECT * FROM products
                                    WHERE id = ? AND owner_id = ?""",
                                 (pid, owner_id)).fetchone()
            else:
                r = conn.execute("SELECT * FROM products WHERE id = ?",
                                 (pid,)).fetchone()
            return dict(r) if r else None

    def update_product(self, pid, owner_id, **kwargs):
        allowed = ["name", "category", "quantity", "price", "min_stock"]
        fields, values = [], []
        for k, v in kwargs.items():
            if k in allowed:
                fields.append(k + " = ?")
                values.append(v)
        if not fields:
            return False
        fields.append("updated_at = ?")
        values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        values.extend([pid, owner_id])
        with self.connect() as conn:
            conn.execute("UPDATE products SET " + ", ".join(fields) +
                         " WHERE id = ? AND owner_id = ?", values)
        return True

    def delete_product(self, pid, owner_id):
        with self.connect() as conn:
            c = conn.execute("DELETE FROM products WHERE id = ? AND owner_id = ?",
                             (pid, owner_id))
            return c.rowcount > 0

    # ================= CUSTOMERS =================
    def create_customer(self, phone, password_hash, name, district=""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO customers
                (phone, password_hash, name, district, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (phone, password_hash, name, district, now))
            return c.lastrowid

    def get_customer(self, phone):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM customers WHERE phone = ?",
                             (phone,)).fetchone()
            return dict(r) if r else None

    def get_customer_by_id(self, cid):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM customers WHERE id = ?",
                             (cid,)).fetchone()
            return dict(r) if r else None

    def add_bonus(self, customer_id, points):
        with self.connect() as conn:
            conn.execute("""UPDATE customers SET bonus_points = bonus_points + ?
                            WHERE id = ?""", (points, customer_id))

    def spend_bonus(self, customer_id, points):
        with self.connect() as conn:
            r = conn.execute("SELECT bonus_points FROM customers WHERE id = ?",
                             (customer_id,)).fetchone()
            if not r or r["bonus_points"] < points:
                return False
            conn.execute("""UPDATE customers SET bonus_points = bonus_points - ?
                            WHERE id = ?""", (points, customer_id))
            return True

    # ================= ORDERS =================
    def create_order(self, customer_id, items, address="", comment="",
                     bonus_spent=0):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = sum(i["price"] * i["quantity"] for i in items)
        bonus_discount = bonus_spent * 1.0
        final = max(0, total - bonus_discount)
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO orders
                (customer_id, address, total_amount, bonus_spent, status,
                 comment, created_at)
                VALUES (?, ?, ?, ?, 'new', ?, ?)""",
                (customer_id, address, final, bonus_spent, comment, now))
            oid = c.lastrowid
            for it in items:
                subtotal = it["price"] * it["quantity"]
                c.execute("""INSERT INTO order_items
                    (order_id, product_id, product_name, product_price,
                     quantity, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (oid, it.get("product_id"), it["name"], it["price"],
                     it["quantity"], subtotal))
            if bonus_spent > 0:
                c.execute("""UPDATE customers
                             SET bonus_points = bonus_points - ?
                             WHERE id = ?""", (bonus_spent, customer_id))
            return oid

    def get_orders(self, customer_id=None, status=None, limit=100):
        q = """SELECT o.*, c.name as customer_name, c.phone as customer_phone,
                      u.full_name as staff_name
               FROM orders o
               JOIN customers c ON o.customer_id = c.id
               LEFT JOIN users u ON o.taken_by = u.id
               WHERE 1=1"""
        params = []
        if customer_id:
            q += " AND o.customer_id = ?"
            params.append(customer_id)
        if status:
            q += " AND o.status = ?"
            params.append(status)
        q += " ORDER BY o.created_at DESC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def get_order(self, oid):
        with self.connect() as conn:
            r = conn.execute("""SELECT o.*, c.name as customer_name,
                                       c.phone as customer_phone,
                                       u.full_name as staff_name
                                FROM orders o
                                JOIN customers c ON o.customer_id = c.id
                                LEFT JOIN users u ON o.taken_by = u.id
                                WHERE o.id = ?""", (oid,)).fetchone()
            if not r:
                return None
            order = dict(r)
            items = conn.execute("""SELECT * FROM order_items
                                    WHERE order_id = ?""", (oid,)).fetchall()
            order["items"] = [dict(i) for i in items]
            return order

    def take_order(self, oid, staff_id):
        with self.connect() as conn:
            c = conn.cursor()
            r = c.execute("SELECT status FROM orders WHERE id = ?",
                          (oid,)).fetchone()
            if not r or r["status"] != "new":
                return False
            c.execute("""UPDATE orders SET status = 'taken', taken_by = ?
                         WHERE id = ?""", (staff_id, oid))
            return c.rowcount > 0

    def mark_delivered(self, oid, staff_id):
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""UPDATE orders SET status = 'delivered'
                         WHERE id = ? AND taken_by = ? AND status = 'taken'""",
                      (oid, staff_id))
            if c.rowcount == 0:
                return False
            r = c.execute("SELECT customer_id, total_amount FROM orders WHERE id = ?",
                          (oid,)).fetchone()
            if r:
                points = int(r["total_amount"] * 0.01)
                if points > 0:
                    c.execute("""UPDATE customers
                                 SET bonus_points = bonus_points + ?
                                 WHERE id = ?""",
                              (points, r["customer_id"]))
            return True

    # ================= CHAT =================
    def add_chat_message(self, order_id, sender_type, sender_name, message):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO chat_messages
                (order_id, sender_type, sender_name, message, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (order_id, sender_type, sender_name, message, now))
            return c.lastrowid

    def get_chat_messages(self, order_id):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("""SELECT * FROM chat_messages
                WHERE order_id = ? ORDER BY created_at""",
                (order_id,)).fetchall()]

    # ================= NOTIFICATIONS =================
    def add_notification(self, user_id, title, body=""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO user_notifications
                (user_id, title, body, created_at)
                VALUES (?, ?, ?, ?)""", (user_id, title, body, now))
            return c.lastrowid

    def get_notifications(self, user_id, limit=30):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("""SELECT * FROM user_notifications
                WHERE user_id = ? ORDER BY created_at DESC LIMIT ?""",
                (user_id, limit)).fetchall()]

    # ================= SALES =================
    def add_sale(self, seller_id, product_id, product_name, quantity,
                 base_price, commission_rate, expected_amount, actual_amount,
                 comment=""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        is_correct = 1 if abs(actual_amount - expected_amount) < 0.01 else 0
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO sales
                (seller_id, product_id, product_name, quantity, base_price,
                 commission_rate, expected_amount, actual_amount, is_correct,
                 comment, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
                (seller_id, product_id, product_name, quantity, base_price,
                 commission_rate, expected_amount, actual_amount, is_correct,
                 comment, now))
            return c.lastrowid

    def get_sales(self, seller_ids=None, status=None):
        q = """SELECT s.*, u.full_name as seller_name,
                      u.username as seller_username
               FROM sales s
               JOIN users u ON s.seller_id = u.id
               WHERE 1=1"""
        params = []
        if seller_ids:
            ph = ",".join("?" * len(seller_ids))
            q += " AND s.seller_id IN (" + ph + ")"
            params.extend(seller_ids)
        if status:
            q += " AND s.status = ?"
            params.append(status)
        q += " ORDER BY s.created_at DESC"
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def get_sale(self, sid):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM sales WHERE id = ?", (sid,)).fetchone()
            return dict(r) if r else None

    def approve_sale(self, sid, reviewer_id, approve=True, comment=""):
        status = "approved" if approve else "rejected"
        with self.connect() as conn:
            conn.execute("""UPDATE sales SET status = ?, reviewed_by = ?,
                            comment = ? WHERE id = ?""",
                         (status, reviewer_id, comment, sid))

    # ================= DEFECTS =================
    def add_defect(self, seller_id, product_id, product_name, quantity, reason=""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO defects
                (seller_id, product_id, product_name, quantity, reason,
                 status, created_at)
                VALUES (?, ?, ?, ?, ?, 'pending', ?)""",
                (seller_id, product_id, product_name, quantity, reason, now))
            return c.lastrowid

    def get_defects(self, seller_ids=None, status=None):
        q = """SELECT d.*, u.full_name as seller_name,
                      u.username as seller_username
               FROM defects d
               JOIN users u ON d.seller_id = u.id
               WHERE 1=1"""
        params = []
        if seller_ids:
            ph = ",".join("?" * len(seller_ids))
            q += " AND d.seller_id IN (" + ph + ")"
            params.extend(seller_ids)
        if status:
            q += " AND d.status = ?"
            params.append(status)
        q += " ORDER BY d.created_at DESC"
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def get_defect(self, did):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM defects WHERE id = ?", (did,)).fetchone()
            return dict(r) if r else None

    def review_defect(self, did, reviewer_id, approve=True, comment=""):
        status = "approved" if approve else "rejected"
        with self.connect() as conn:
            conn.execute("""UPDATE defects SET status = ?, reviewed_by = ?,
                            review_comment = ? WHERE id = ?""",
                         (status, reviewer_id, comment, did))

    # ================= TRANSFERS =================
    def add_transfer(self, from_user_id, to_user_id, product_id, product_name,
                     quantity, comment, initiated_by, requires_admin=0):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO transfers
                (from_user_id, to_user_id, product_id, product_name, quantity,
                 comment, status, initiated_by, requires_admin, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)""",
                (from_user_id, to_user_id, product_id, product_name, quantity,
                 comment, initiated_by, requires_admin, now))
            return c.lastrowid

    def get_transfers(self, user_ids=None, status=None):
        q = """SELECT t.*,
                      fu.full_name as from_name, fu.username as from_username,
                      tu.full_name as to_name, tu.username as to_username
               FROM transfers t
               JOIN users fu ON t.from_user_id = fu.id
               JOIN users tu ON t.to_user_id = tu.id
               WHERE 1=1"""
        params = []
        if user_ids:
            ph = ",".join("?" * len(user_ids))
            q += " AND (t.from_user_id IN (" + ph + ") OR t.to_user_id IN (" + ph + "))"
            params.extend(user_ids * 2)
        if status:
            q += " AND t.status = ?"
            params.append(status)
        q += " ORDER BY t.created_at DESC"
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def get_transfer(self, tid):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM transfers WHERE id = ?", (tid,)).fetchone()
            return dict(r) if r else None

    def approve_transfer(self, tid, approver_id):
        with self.connect() as conn:
            c = conn.cursor()
            t = c.execute("SELECT * FROM transfers WHERE id = ?", (tid,)).fetchone()
            if not t or t["status"] != "pending":
                return False
            src = c.execute("""SELECT * FROM products
                               WHERE id = ? AND owner_id = ?""",
                            (t["product_id"], t["from_user_id"])).fetchone()
            if not src or src["quantity"] < t["quantity"]:
                return False
            c.execute("""UPDATE products SET quantity = quantity - ?
                         WHERE id = ?""", (t["quantity"], t["product_id"]))
            existing = c.execute("""SELECT * FROM products
                                    WHERE owner_id = ? AND name = ?""",
                                 (t["to_user_id"], src["name"])).fetchone()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if existing:
                c.execute("""UPDATE products SET quantity = quantity + ?
                             WHERE id = ?""",
                          (t["quantity"], existing["id"]))
            else:
                c.execute("""INSERT INTO products
                    (owner_id, name, category, quantity, price, min_stock,
                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (t["to_user_id"], src["name"], src["category"],
                     t["quantity"], src["price"], src["min_stock"], now, now))
            c.execute("""UPDATE transfers SET status = 'completed',
                        approved_by = ? WHERE id = ?""", (approver_id, tid))
            return True

    def reject_transfer(self, tid, approver_id, comment=""):
        with self.connect() as conn:
            conn.execute("""UPDATE transfers SET status = 'rejected',
                            approved_by = ?, comment = ? WHERE id = ?""",
                         (approver_id, comment, tid))

    # ================= REVISIONS =================
    def create_revision(self, requester_id, target_user_id, comment=""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO revisions
                (requester_id, target_user_id, status, comment, created_at)
                VALUES (?, ?, 'requested', ?, ?)""",
                (requester_id, target_user_id, comment, now))
            return c.lastrowid

    def get_revisions(self, user_ids=None, status=None):
        q = """SELECT r.*,
                      req.full_name as requester_name,
                      tgt.full_name as target_name, tgt.username as target_username
               FROM revisions r
               JOIN users req ON r.requester_id = req.id
               JOIN users tgt ON r.target_user_id = tgt.id
               WHERE 1=1"""
        params = []
        if user_ids:
            ph = ",".join("?" * len(user_ids))
            q += " AND (r.target_user_id IN (" + ph + ") OR r.requester_id IN (" + ph + "))"
            params.extend(user_ids * 2)
        if status:
            q += " AND r.status = ?"
            params.append(status)
        q += " ORDER BY r.created_at DESC"
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def get_revision(self, rid):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM revisions WHERE id = ?", (rid,)).fetchone()
            return dict(r) if r else None

    def add_revision_item(self, revision_id, product_id, product_name,
                          expected_qty, actual_qty):
        with self.connect() as conn:
            conn.execute("""INSERT INTO revision_items
                (revision_id, product_id, product_name, expected_qty,
                 actual_qty, diff)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (revision_id, product_id, product_name, expected_qty,
                 actual_qty, actual_qty - expected_qty))

    def get_revision_items(self, revision_id):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("""SELECT * FROM revision_items
                WHERE revision_id = ?""", (revision_id,)).fetchall()]

    def complete_revision(self, rid, comment=""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            conn.execute("""UPDATE revisions SET status = 'completed',
                            result_comment = ?, completed_at = ?
                            WHERE id = ?""", (comment, now, rid))
    def dashboard_stats(self, days=30):
        with self.connect() as conn:
            r = conn.execute("SELECT COUNT(*) as total_orders, SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) as delivered, COALESCE(SUM(CASE WHEN status='delivered' THEN total_amount ELSE 0 END), 0) as revenue FROM orders").fetchone()
            return dict(r) if r else {}

    def top_products(self, days=30, limit=10):
        with self.connect() as conn:
            rows = conn.execute("SELECT oi.product_name, SUM(oi.quantity) as qty, SUM(oi.subtotal) as revenue FROM order_items oi JOIN orders o ON oi.order_id = o.id WHERE o.status='delivered' GROUP BY oi.product_name ORDER BY revenue DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def top_sellers(self, days=30, limit=10):
        with self.connect() as conn:
            rows = conn.execute("SELECT u.username, u.full_name, COUNT(*) as count, COALESCE(SUM(o.total_amount), 0) as revenue FROM orders o JOIN users u ON o.taken_by = u.id WHERE o.status='delivered' GROUP BY u.id ORDER BY revenue DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def list_zones(self):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM delivery_zones ORDER BY name").fetchall()]

    def add_zone(self, name, fee, free_from=0, eta=60):
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO delivery_zones (name, delivery_fee, free_from, eta_minutes, created_at) VALUES (?, ?, ?, ?, datetime('now'))", (name, fee, free_from, eta))
            return c.lastrowid

    def list_missions(self):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM missions WHERE is_active=1 ORDER BY sort_order").fetchall()]

    def list_product_images(self, product_id):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM product_images WHERE product_id=? ORDER BY id", (product_id,)).fetchall()]

    def kpi_leaderboard(self, days=30):
        with self.connect() as conn:
            rows = conn.execute("SELECT u.id, u.username, u.full_name, u.role, COUNT(s.id) as sales_count, COALESCE(SUM(s.actual_amount), 0) as revenue FROM users u LEFT JOIN sales s ON s.seller_id = u.id AND s.status='approved' WHERE u.role IN ('seller','mentor') GROUP BY u.id ORDER BY revenue DESC").fetchall()
            result = []
            for i, r in enumerate(rows, 1):
                d = dict(r)
                d['rank'] = i
                d['accuracy'] = 100
                result.append(d)
            return result


    # ================= MISSIONS V2 =================
    def create_mission_full(self, code, title, description, icon,
                             mission_category, target_value, reward_value,
                             action_url="", platform="", verify_hint="",
                             repeat_type="once", requires_approval=0,
                             is_active=1):
        """Создать миссию с полными параметрами"""
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO missions
                (code, title, description, icon, mission_category,
                 target_value, reward_value, action_url, platform,
                 verify_hint, repeat_type, requires_approval,
                 is_active, sort_order, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, datetime('now'))""",
                (code, title, description, icon, mission_category,
                 target_value, reward_value, action_url, platform,
                 verify_hint, repeat_type, requires_approval, is_active))
            return c.lastrowid

    def list_missions_admin(self):
        """Все миссии включая неактивные"""
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM missions ORDER BY id DESC"
            ).fetchall()]

    def get_customer_mission_progress(self, customer_id, mission_id):
        with self.connect() as conn:
            r = conn.execute("""SELECT * FROM customer_mission_progress
                                WHERE customer_id=? AND mission_id=?""",
                             (customer_id, mission_id)).fetchone()
            return dict(r) if r else None

    def start_mission(self, customer_id, mission_id):
        """Клиент начинает миссию"""
        with self.connect() as conn:
            c = conn.cursor()
            r = c.execute("""SELECT id FROM customer_mission_progress
                             WHERE customer_id=? AND mission_id=?""",
                          (customer_id, mission_id)).fetchone()
            if r:
                return r["id"]
            c.execute("""INSERT INTO customer_mission_progress
                (customer_id, mission_id, current_value, status, started_at)
                VALUES (?, ?, 0, 'in_progress', datetime('now'))""",
                (customer_id, mission_id))
            return c.lastrowid

    def complete_mission_customer(self, customer_id, mission_id,
                                   proof_text="", proof_url=""):
        """Клиент отмечает миссию выполненной"""
        with self.connect() as conn:
            c = conn.cursor()
            r = c.execute("""SELECT * FROM customer_mission_progress
                             WHERE customer_id=? AND mission_id=?""",
                          (customer_id, mission_id)).fetchone()
            if not r:
                c.execute("""INSERT INTO customer_mission_progress
                    (customer_id, mission_id, current_value, status,
                     proof_text, proof_url, started_at, completed_at)
                    VALUES (?, ?, 1, 'pending_approval', ?, ?,
                            datetime('now'), datetime('now'))""",
                    (customer_id, mission_id, proof_text, proof_url))
            else:
                c.execute("""UPDATE customer_mission_progress
                    SET status='pending_approval', proof_text=?,
                        proof_url=?, completed_at=datetime('now')
                    WHERE id=?""",
                    (proof_text, proof_url, r["id"]))
            return True

    def approve_mission_customer(self, progress_id, approve=True):
        """Админ подтверждает выполнение"""
        with self.connect() as conn:
            c = conn.cursor()
            status = "completed" if approve else "rejected"
            c.execute("""UPDATE customer_mission_progress
                         SET status=?, is_completed=?
                         WHERE id=?""",
                      (status, 1 if approve else 0, progress_id))

            if approve:
                r = c.execute("""SELECT * FROM customer_mission_progress
                                 WHERE id=?""", (progress_id,)).fetchone()
                if r:
                    m = c.execute("SELECT * FROM missions WHERE id=?",
                                  (r["mission_id"],)).fetchone()
                    if m:
                        c.execute("""UPDATE customers
                                     SET bonus_points = bonus_points + ?
                                     WHERE id=?""",
                                  (m["reward_value"], r["customer_id"]))
                        c.execute("""UPDATE customer_mission_progress
                                     SET is_claimed=1, claimed_at=datetime('now')
                                     WHERE id=?""", (progress_id,))
            return True

    def get_pending_missions(self):
        """Список миссий ожидающих подтверждения"""
        with self.connect() as conn:
            rows = conn.execute("""
                SELECT cmp.*, c.name as customer_name, c.phone as customer_phone,
                       m.title, m.icon, m.reward_value, m.mission_category
                FROM customer_mission_progress cmp
                JOIN customers c ON cmp.customer_id = c.id
                JOIN missions m ON cmp.mission_id = m.id
                WHERE cmp.status = 'pending_approval'
                ORDER BY cmp.completed_at DESC
            """).fetchall()
            return [dict(r) for r in rows]

    def get_visible_missions(self, customer_id):
        """Только те миссии, которые ещё НЕ выполнены полностью"""
        import time
        from datetime import datetime
        
        with self.connect() as conn:
            rows = conn.execute("""
                SELECT m.*,
                       COALESCE(cmp.current_value, 0) as user_current,
                       COALESCE(cmp.is_completed, 0) as is_completed,
                       COALESCE(cmp.is_claimed, 0) as is_claimed,
                       COALESCE(cmp.status, 'not_started') as user_status,
                       cmp.period_key as user_period
                FROM missions m
                LEFT JOIN customer_mission_progress cmp
                  ON cmp.mission_id = m.id AND cmp.customer_id = ?
                WHERE m.is_active = 1
                ORDER BY m.id DESC
            """, (customer_id,)).fetchall()
        
        result = []
        now = datetime.now()
        for r in rows:
            d = dict(r)
            m = d
            
            # Вычисляем текущий period_key для повторяемых
            repeat = m.get("repeat_type") or "once"
            if repeat == "daily":
                current_period = now.strftime("%Y-%m-%d")
            elif repeat == "weekly":
                current_period = now.strftime("%Y-W%W")
            elif repeat == "monthly":
                current_period = now.strftime("%Y-%m")
            else:
                current_period = "once"
            
            user_period = d.get("user_period")
            user_current = d.get("user_current") or 0
            
            # Если период изменился — сбрасываем прогресс
            if repeat != "once" and user_period and user_period != current_period:
                user_current = 0
                user_period = current_period
            
            # Показывать ли миссию
            target = m["target_value"] or 1
            
            # Уже выполнена полностью?
            if repeat == "once" and user_current >= target:
                continue
            
            # Не показываем уже завершённые (которые не надо повторять)
            if d.get("is_claimed") and repeat == "once":
                continue
            
            # Показываем
            d["user_current"] = user_current
            d["progress_percent"] = min(100, int(user_current / target * 100))
            d["remaining"] = max(0, target - user_current)
            result.append(d)
        
        return result

    def increment_mission(self, customer_id, mission_id, proof_text="", proof_url=""):
        """Увеличить счётчик выполнения миссии на 1"""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with self.connect() as conn:
            c = conn.cursor()
            
            # Получаем миссию
            m = c.execute("SELECT * FROM missions WHERE id = ?", (mission_id,)).fetchone()
            if not m:
                return None
            
            # period_key
            repeat = m["repeat_type"] or "once"
            if repeat == "daily":
                period_key = datetime.now().strftime("%Y-%m-%d")
            elif repeat == "weekly":
                period_key = datetime.now().strftime("%Y-W%W")
            elif repeat == "monthly":
                period_key = datetime.now().strftime("%Y-%m")
            else:
                period_key = "once"
            
            # Есть ли запись?
            r = c.execute("""SELECT * FROM customer_mission_progress
                             WHERE customer_id=? AND mission_id=?""",
                          (customer_id, mission_id)).fetchone()
            
            target = m["target_value"] or 1
            
            if not r:
                # Создаём новую
                new_value = 1
                c.execute("""INSERT INTO customer_mission_progress
                    (customer_id, mission_id, current_value, period_key,
                     proof_text, proof_url, last_action_at, started_at,
                     status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (customer_id, mission_id, new_value, period_key,
                     proof_text, proof_url, now, now,
                     'pending_approval' if m["requires_approval"] else 'in_progress'))
                progress_id = c.lastrowid
            else:
                # Обновляем
                if repeat != "once" and r["period_key"] != period_key:
                    new_value = 1
                else:
                    new_value = (r["current_value"] or 0) + 1
                
                is_done = 1 if new_value >= target else 0
                
                c.execute("""UPDATE customer_mission_progress
                    SET current_value=?, period_key=?,
                        is_completed=?, proof_text=?, proof_url=?,
                        last_action_at=?, completed_at=?,
                        status=?
                    WHERE id=?""",
                    (new_value, period_key, is_done,
                     proof_text, proof_url, now,
                     now if is_done else None,
                     'pending_approval' if m["requires_approval"] else 'in_progress',
                     r["id"]))
                progress_id = r["id"]
            
            # Проверяем завершение
            is_final = new_value >= target
            
            # Если не требует подтверждения — сразу начисляем награду
            if is_final and not m["requires_approval"]:
                c.execute("""UPDATE customers
                             SET bonus_points = bonus_points + ?
                             WHERE id=?""",
                          (m["reward_value"], customer_id))
                c.execute("""UPDATE customer_mission_progress
                             SET is_claimed=1, claimed_at=?, status='completed'
                             WHERE id=?""", (now, progress_id))
            
            return {
                "progress_id": progress_id,
                "current": new_value,
                "target": target,
                "is_completed": is_final,
                "reward": m["reward_value"] if is_final else 0,
                "needs_approval": bool(m["requires_approval"]),
            }


    def get_mission_by_code(self, code):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM missions WHERE code = ?",
                             (code,)).fetchone()
            return dict(r) if r else None

    def get_mission(self, mid):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM missions WHERE id = ?",
                             (mid,)).fetchone()
            return dict(r) if r else None

    def list_missions(self):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM missions WHERE is_active=1 ORDER BY id DESC"
            ).fetchall()]

    def create_mission(self, code, title, description="", icon="X",
                        mission_type="orders_count", target_value=1,
                        reward_value=100, created_by=None,
                        repeat_type="once", **kwargs):
        """Простая версия для обратной совместимости"""
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO missions
                (code, title, description, icon, mission_type,
                 target_value, reward_value, repeat_type,
                 is_active, sort_order, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 0, datetime('now'))""",
                (code, title, description, icon, mission_type,
                 target_value, reward_value, repeat_type))
            return c.lastrowid

    def delete_mission(self, mid):
        with self.connect() as conn:
            conn.execute("DELETE FROM missions WHERE id = ?", (mid,))
            conn.execute("DELETE FROM customer_mission_progress WHERE mission_id = ?", (mid,))


    # ================= CUSTOMER PROFILE =================
    def get_customer_stats(self, customer_id):
        with self.connect() as conn:
            r = conn.execute("""
                SELECT
                    COUNT(*) as total_orders,
                    SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) as delivered,
                    SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) as cancelled,
                    COALESCE(SUM(CASE WHEN status='delivered' THEN total_amount ELSE 0 END), 0) as total_spent
                FROM orders
                WHERE customer_id = ?
            """, (customer_id,)).fetchone()
            d = dict(r) if r else {}
            delivered = d.get("delivered") or 0
            spent = d.get("total_spent") or 0
            d["avg_check"] = round(spent / delivered, 2) if delivered else 0
            return d

    def get_customer_orders(self, customer_id, limit=50):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("""
                SELECT * FROM orders
                WHERE customer_id = ?
                ORDER BY created_at DESC LIMIT ?
            """, (customer_id, limit)).fetchall()]

    def get_customer_missions_progress(self, customer_id):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("""
                SELECT m.*,
                       COALESCE(cmp.current_value, 0) as user_current,
                       COALESCE(cmp.status, 'not_started') as user_status,
                       cmp.claimed_at
                FROM missions m
                LEFT JOIN customer_mission_progress cmp
                  ON cmp.mission_id = m.id AND cmp.customer_id = ?
                WHERE m.is_active = 1
                ORDER BY m.id DESC
            """, (customer_id,)).fetchall()]


    # ================= BANK ACCOUNTS =================
    def list_bank_accounts(self, active_only=False):
        with self.connect() as conn:
            q = "SELECT * FROM bank_accounts"
            if active_only:
                q += " WHERE is_active = 1"
            q += " ORDER BY id"
            return [dict(r) for r in conn.execute(q).fetchall()]

    def get_bank_account(self, aid):
        with self.connect() as conn:
            r = conn.execute("SELECT * FROM bank_accounts WHERE id = ?",
                             (aid,)).fetchone()
            return dict(r) if r else None

    def create_bank_account(self, name, bank="", account_number=""):
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO bank_accounts
                (name, bank, account_number, balance, is_active, created_at)
                VALUES (?, ?, ?, 0, 1, ?)""",
                (name, bank, account_number, now))
            return c.lastrowid

    def update_bank_account(self, aid, **kwargs):
        allowed = ["name", "bank", "account_number", "balance", "is_active"]
        fields, values = [], []
        for k, v in kwargs.items():
            if k in allowed:
                fields.append(k + " = ?")
                values.append(v)
        if not fields:
            return False
        values.append(aid)
        with self.connect() as conn:
            conn.execute("UPDATE bank_accounts SET " + ", ".join(fields) +
                         " WHERE id = ?", values)
        return True

    def delete_bank_account(self, aid):
        with self.connect() as conn:
            # Проверяем есть ли транзакции
            r = conn.execute("SELECT COUNT(*) FROM transactions WHERE account_id = ?",
                             (aid,)).fetchone()
            if r and r[0] > 0:
                # Нельзя удалить - отключаем
                conn.execute("UPDATE bank_accounts SET is_active = 0 WHERE id = ?", (aid,))
                return "deactivated"
            else:
                conn.execute("DELETE FROM bank_accounts WHERE id = ?", (aid,))
                return "deleted"

    def get_total_balance(self):
        with self.connect() as conn:
            r = conn.execute("SELECT COALESCE(SUM(balance), 0) FROM bank_accounts WHERE is_active = 1").fetchone()
            return r[0] if r else 0

    # ================= TRANSACTIONS =================
    def create_transaction(self, account_id, ttype, amount, order_id=None,
                            seller_id=None, requester_id=None, comment=""):
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO transactions
                (account_id, type, amount, order_id, seller_id, requester_id,
                 status, comment, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
                (account_id, ttype, amount, order_id, seller_id, requester_id,
                 comment, now))
            return c.lastrowid

    def list_transactions(self, status=None, ttype=None, limit=200):
        q = """SELECT t.*,
                      a.name as account_name,
                      s.full_name as seller_name, s.username as seller_username,
                      rq.full_name as requester_name,
                      rev.full_name as reviewer_name,
                      o.id as order_num
               FROM transactions t
               LEFT JOIN bank_accounts a ON t.account_id = a.id
               LEFT JOIN users s ON t.seller_id = s.id
               LEFT JOIN users rq ON t.requester_id = rq.id
               LEFT JOIN users rev ON t.reviewer_id = rev.id
               LEFT JOIN orders o ON t.order_id = o.id
               WHERE 1=1"""
        params = []
        if status:
            q += " AND t.status = ?"
            params.append(status)
        if ttype:
            q += " AND t.type = ?"
            params.append(ttype)
        q += " ORDER BY t.created_at DESC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def get_transaction(self, tid):
        with self.connect() as conn:
            r = conn.execute("""
                SELECT t.*,
                       a.name as account_name,
                       a.bank as account_bank,
                       a.account_number as account_number,
                       s.full_name as seller_name,
                       rq.full_name as requester_name,
                       rev.full_name as reviewer_name
                FROM transactions t
                LEFT JOIN bank_accounts a ON t.account_id = a.id
                LEFT JOIN users s ON t.seller_id = s.id
                LEFT JOIN users rq ON t.requester_id = rq.id
                LEFT JOIN users rev ON t.reviewer_id = rev.id
                WHERE t.id = ?""", (tid,)).fetchone()
            return dict(r) if r else None

    def approve_transaction(self, tid, reviewer_id, approve=True, comment=""):
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            t = c.execute("SELECT * FROM transactions WHERE id = ?", (tid,)).fetchone()
            if not t:
                return False
            if t["status"] != "pending":
                return False

            if approve:
                # Меняем баланс
                if t["type"] == "income":
                    c.execute("UPDATE bank_accounts SET balance = balance + ? WHERE id = ?",
                              (t["amount"], t["account_id"]))
                else:  # expense
                    c.execute("UPDATE bank_accounts SET balance = balance - ? WHERE id = ?",
                              (t["amount"], t["account_id"]))

                # Если это поступление от заказа — обновляем заказ
                if t["order_id"]:
                    c.execute("""UPDATE orders SET
                        payment_status = 'paid',
                        paid_to_account_id = ?,
                        paid_amount = ?,
                        paid_at = ?
                        WHERE id = ?""",
                        (t["account_id"], t["amount"], now, t["order_id"]))

                new_status = "approved"
            else:
                new_status = "rejected"

            c.execute("""UPDATE transactions SET
                status = ?, reviewer_id = ?, review_comment = ?, reviewed_at = ?
                WHERE id = ?""", (new_status, reviewer_id, comment, now, tid))
            return True

    def get_pending_transactions_count(self):
        with self.connect() as conn:
            r = conn.execute("SELECT COUNT(*) FROM transactions WHERE status = 'pending'").fetchone()
            return r[0] if r else 0

    # ================= DELIVERED ITEMS =================
    def save_delivered_items(self, order_id, items):
        """items = [{"product_id": 1, "product_name": "X", "quantity_ordered": 2, "quantity_delivered": 2}]"""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            # Удаляем старые
            c.execute("DELETE FROM order_items_delivered WHERE order_id = ?", (order_id,))
            # Добавляем новые
            for it in items:
                c.execute("""INSERT INTO order_items_delivered
                    (order_id, product_id, product_name, quantity_ordered,
                     quantity_delivered, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (order_id, it.get("product_id"), it.get("product_name"),
                     it.get("quantity_ordered"), it.get("quantity_delivered"),
                     now))

    def get_delivered_items(self, order_id):
        with self.connect() as conn:
            return [dict(r) for r in conn.execute("""
                SELECT * FROM order_items_delivered
                WHERE order_id = ?
                ORDER BY id
            """, (order_id,)).fetchall()]

    def get_finance_stats(self):
        """Общая статистика финансов"""
        with self.connect() as conn:
            total = conn.execute("SELECT COALESCE(SUM(balance), 0) FROM bank_accounts WHERE is_active = 1").fetchone()[0]
            income = conn.execute("""SELECT COALESCE(SUM(amount), 0) FROM transactions
                                     WHERE type = 'income' AND status = 'approved'""").fetchone()[0]
            expense = conn.execute("""SELECT COALESCE(SUM(amount), 0) FROM transactions
                                      WHERE type = 'expense' AND status = 'approved'""").fetchone()[0]
            pending = conn.execute("SELECT COUNT(*) FROM transactions WHERE status = 'pending'").fetchone()[0]
            return {
                "total": total or 0,
                "income": income or 0,
                "expense": expense or 0,
                "pending_count": pending or 0,
            }


    def get_finance_dashboard_stats(self, days=30):
        """Статистика для дашборда админа"""
        from datetime import datetime, timedelta
        with self.connect() as conn:
            # Всего
            total = conn.execute("SELECT COALESCE(SUM(balance), 0) FROM bank_accounts WHERE is_active = 1").fetchone()[0] or 0

            # За период
            r = conn.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN type='income' AND status='approved' THEN amount ELSE 0 END), 0) as income,
                    COALESCE(SUM(CASE WHEN type='expense' AND status='approved' THEN amount ELSE 0 END), 0) as expense,
                    COUNT(CASE WHEN status='pending' THEN 1 END) as pending
                FROM transactions
                WHERE created_at >= DATE('now', ?)
            """, (f'-{days} days',)).fetchone()

            # По дням за последние 7 дней
            by_day = [dict(r) for r in conn.execute("""
                SELECT DATE(created_at) as day,
                       SUM(CASE WHEN type='income' AND status='approved' THEN amount ELSE 0 END) as income,
                       SUM(CASE WHEN type='expense' AND status='approved' THEN amount ELSE 0 END) as expense
                FROM transactions
                WHERE created_at >= DATE('now', '-7 days')
                GROUP BY day ORDER BY day
            """).fetchall()]

            return {
                "total": total,
                "income": r["income"] if r else 0,
                "expense": r["expense"] if r else 0,
                "pending": r["pending"] if r else 0,
                "by_day": by_day,
            }


    # ================= ORDER MODIFICATION =================
    def update_order_items(self, order_id, new_items, new_total):
        """Заменяет состав заказа и пересчитывает итог"""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            c = conn.cursor()
            # Удаляем старые позиции
            c.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
            # Добавляем новые
            for it in new_items:
                subtotal = it["price"] * it["quantity"]
                c.execute("""INSERT INTO order_items
                    (order_id, product_id, product_name, product_price,
                     quantity, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (order_id, it.get("product_id"), it["name"],
                     it["price"], it["quantity"], subtotal))
            # Обновляем сумму заказа
            c.execute("""UPDATE orders SET total_amount = ?, updated_at = ?
                         WHERE id = ?""", (new_total, now, order_id))

    def add_order_history(self, order_id, action, actor_type, actor_id,
                           actor_name, comment=""):
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            conn.execute("""INSERT INTO order_history
                (order_id, action, actor_type, actor_id, actor_name, comment, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (order_id, action, actor_type, actor_id, actor_name, comment, now))


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
