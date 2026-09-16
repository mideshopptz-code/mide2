# -*- coding: utf-8 -*-
import sqlite3

print("1. Updating DB schema...")

conn = sqlite3.connect("warehouse.db")
c = conn.cursor()

# Проверяем какие колонки есть в missions
cols = [r[1] for r in c.execute("PRAGMA table_info(missions)").fetchall()]
print("   Current cols:", cols)

# Добавляем новые колонки
new_cols = [
    ("mission_category", "TEXT"),      # buy / subscribe / invite / post / task
    ("action_url", "TEXT"),            # куда подписаться / ссылка
    ("platform", "TEXT"),              # instagram / vk / telegram / youtube / other
    ("verify_hint", "TEXT"),           # подсказка для проверки
    ("repeat_type", "TEXT DEFAULT 'once'"),
    ("requires_approval", "INTEGER DEFAULT 0"),  # нужна ли проверка админом
]

for col, ddl in new_cols:
    if col not in cols:
        try:
            c.execute(f"ALTER TABLE missions ADD COLUMN {col} {ddl}")
            print(f"   + {col}")
        except Exception as e:
            print(f"   ! {col}: {e}")

# Таблица выполнения миссий покупателями
c.execute("""CREATE TABLE IF NOT EXISTS customer_mission_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    mission_id INTEGER NOT NULL,
    current_value INTEGER DEFAULT 0,
    is_completed INTEGER DEFAULT 0,
    is_claimed INTEGER DEFAULT 0,
    proof_text TEXT,
    proof_url TEXT,
    status TEXT DEFAULT 'in_progress',
    started_at TEXT,
    completed_at TEXT,
    claimed_at TEXT,
    UNIQUE(customer_id, mission_id)
)""")
print("   OK customer_mission_progress table")

conn.commit()
conn.close()
print("   DB updated")
print()

# ============================================================
# Обновляем database.py — методы для миссий
# ============================================================
print("2. Updating database.py...")

EXTRA = '''

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

    def get_customer_all_missions(self, customer_id):
        """Все активные миссии + прогресс клиента"""
        with self.connect() as conn:
            rows = conn.execute("""
                SELECT m.*,
                       COALESCE(cmp.status, 'not_started') as user_status,
                       COALESCE(cmp.is_completed, 0) as is_completed,
                       COALESCE(cmp.is_claimed, 0) as is_claimed,
                       COALESCE(cmp.proof_text, '') as proof_text,
                       COALESCE(cmp.proof_url, '') as proof_url
                FROM missions m
                LEFT JOIN customer_mission_progress cmp
                  ON cmp.mission_id = m.id AND cmp.customer_id = ?
                WHERE m.is_active = 1
                ORDER BY m.id DESC
            """, (customer_id,)).fetchall()
            return [dict(r) for r in rows]
'''

content = open("database.py", encoding="utf-8").read()
if "def create_mission_full" not in content:
    if not content.endswith("\n"):
        content += "\n"
    content += EXTRA
    open("database.py", "w", encoding="utf-8").write(content)
    print("   OK: methods added")
else:
    print("   already exists")

print()
print("Done!")
print("Now run: python add_mission_routes.py (next step)")