# -*- coding: utf-8 -*-
import sqlite3

print("=" * 50)
print("FINANCE SYSTEM - Part 1: Database")
print("=" * 50)
print()

# ============================================================
# 1. СОЗДАЁМ ТАБЛИЦЫ
# ============================================================
print("1. Creating tables...")

conn = sqlite3.connect("warehouse.db")
c = conn.cursor()

# --- Счета компании ---
c.execute("""CREATE TABLE IF NOT EXISTS bank_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    bank TEXT,
    account_number TEXT,
    balance REAL DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT
)""")
print("   OK bank_accounts")

# --- Транзакции ---
c.execute("""CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    order_id INTEGER,
    seller_id INTEGER,
    requester_id INTEGER,
    status TEXT DEFAULT 'pending',
    comment TEXT,
    reviewer_id INTEGER,
    review_comment TEXT,
    created_at TEXT,
    reviewed_at TEXT
)""")
print("   OK transactions")

# --- Что реально доставили в заказе ---
c.execute("""CREATE TABLE IF NOT EXISTS order_items_delivered (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER,
    product_name TEXT,
    quantity_ordered INTEGER,
    quantity_delivered INTEGER,
    created_at TEXT
)""")
print("   OK order_items_delivered")

# --- Добавляем счета по умолчанию если нет ---
c.execute("SELECT COUNT(*) FROM bank_accounts")
if c.fetchone()[0] == 0:
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    accounts = [
        ("Сбербанк", "sberbank", "0000-0000-0000-0001", 0),
        ("Тинькофф", "tinkoff", "0000-0000-0000-0002", 0),
        ("Наличные", "cash", "-", 0),
    ]
    for name, bank, acc, bal in accounts:
        c.execute("""INSERT INTO bank_accounts
            (name, bank, account_number, balance, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)""", (name, bank, acc, bal, now))
    print("   OK: 3 default accounts added")

# --- Обновляем orders — добавляем поля оплаты ---
cols = [r[1] for r in c.execute("PRAGMA table_info(orders)").fetchall()]
new_cols = [
    ("paid_to_account_id", "INTEGER"),
    ("paid_amount", "REAL DEFAULT 0"),
    ("paid_at", "TEXT"),
    ("payment_status", "TEXT DEFAULT 'unpaid'"),
]
for col, ddl in new_cols:
    if col not in cols:
        c.execute(f"ALTER TABLE orders ADD COLUMN {col} {ddl}")
        print(f"   + orders.{col}")

# --- Обновляем users — роль accountant уже поддерживается ---
print("   OK: role 'accountant' ready")

conn.commit()
conn.close()
print()
print("DB updated!")
print()

# ============================================================
# 2. ДОБАВЛЯЕМ МЕТОДЫ В DATABASE.PY
# ============================================================
print("2. Adding methods to database.py...")

METHODS = '''

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
                SELECT t.*, a.name as account_name,
                       s.full_name as seller_name
                FROM transactions t
                LEFT JOIN bank_accounts a ON t.account_id = a.id
                LEFT JOIN users s ON t.seller_id = s.id
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
'''

content = open("database.py", encoding="utf-8").read()
if "def list_bank_accounts" not in content:
    if not content.endswith("\n"):
        content += "\n"
    content += METHODS
    open("database.py", "w", encoding="utf-8").write(content)
    print("   OK methods added (15 new)")
else:
    print("   already exists")

# Проверка синтаксиса
import ast
try:
    ast.parse(open("database.py", encoding="utf-8").read())
    print()
    print("SYNTAX OK!")
except SyntaxError as e:
    print()
    print("SYNTAX ERROR at line", e.lineno, ":", e.msg)

print()
print("=" * 50)
print("DONE! Restart server.")
print("=" * 50)
print()
print("Next: add finance UI (routes + templates)")