# -*- coding: utf-8 -*-
import sqlite3

print("1. Adding new columns...")
conn = sqlite3.connect("warehouse.db")
c = conn.cursor()

cols = [r[1] for r in c.execute("PRAGMA table_info(customer_mission_progress)").fetchall()]
print("   Current:", cols)

new_cols = [
    ("current_value", "INTEGER DEFAULT 0"),
    ("period_key", "TEXT"),
    ("last_action_at", "TEXT"),
]
for col, ddl in new_cols:
    if col not in cols:
        try:
            c.execute(f"ALTER TABLE customer_mission_progress ADD COLUMN {col} {ddl}")
            print(f"   + {col}")
        except Exception as e:
            print(f"   ! {col}: {e}")

conn.commit()
conn.close()
print("   DB updated")
print()

# ============================================================
# Обновляем database.py
# ============================================================
print("2. Updating database.py...")

content = open("database.py", encoding="utf-8").read()

# Заменяем метод get_customer_all_missions — учитываем прогресс и повторяемость
NEW_METHOD = '''

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
'''

# Ищем старый метод и заменяем
old_marker = "    def get_customer_all_missions(self, customer_id):"
if old_marker in content:
    # Удаляем старый метод
    start = content.find(old_marker)
    # Ищем следующий def на том же уровне
    next_def = content.find("\n    def ", start + 10)
    if next_def == -1:
        next_def = len(content)
    content = content[:start] + NEW_METHOD.strip() + "\n\n" + content[next_def:]
    open("database.py", "w", encoding="utf-8").write(content)
    print("   OK: replaced get_customer_all_missions with get_visible_missions")
else:
    # Добавляем как новый
    if "def get_visible_missions" not in content:
        if not content.endswith("\n"):
            content += "\n"
        content += NEW_METHOD
        open("database.py", "w", encoding="utf-8").write(content)
        print("   OK: added get_visible_missions")

print()
print("Done! Now update web_app.py routes (next step).")