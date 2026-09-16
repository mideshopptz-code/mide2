# -*- coding: utf-8 -*-

content = open("database.py", encoding="utf-8").read()

EXTRA = '''

    # ================= MISSIONS (дополнение) =================
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
'''

if "def get_mission_by_code" not in content:
    if not content.endswith("\n"):
        content += "\n"
    content += EXTRA
    open("database.py", "w", encoding="utf-8").write(content)
    print("OK: methods added")
else:
    print("already has get_mission_by_code")

# Проверим
check = open("database.py", encoding="utf-8").read()
print()
print("Check:")
print("  get_mission_by_code:", "def get_mission_by_code" in check)
print("  get_mission:", "def get_mission(" in check)
print("  list_missions:", "def list_missions" in check)
print("  delete_mission:", "def delete_mission" in check)
print("  create_mission_full:", "def create_mission_full" in check)
print()
print("Done! Restart server.")