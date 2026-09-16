# -*- coding: utf-8 -*-
import re

content = open("database.py", encoding="utf-8").read()

# Ищем метод get_transaction
pattern = r'(    def get_transaction\(self, tid\):.*?)(?=\n    def )'
match = re.search(pattern, content, re.DOTALL)

if not match:
    print("ERROR: get_transaction не найден")
    exit()

old_method = match.group(1)
print("Найден старый метод:")
print(old_method[:200])
print("...")
print()

new_method = '''    def get_transaction(self, tid):
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
'''

content = content.replace(old_method, new_method)
open("database.py", "w", encoding="utf-8").write(content)
print("OK: метод заменён")

# Проверка
c = open("database.py", encoding="utf-8").read()
print()
print("Проверка:")
print("  account_number as account_number:", "account_number as account_number" in c)
print("  account_bank as account_bank:", "account_bank as account_bank" in c)

# Синтаксис
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