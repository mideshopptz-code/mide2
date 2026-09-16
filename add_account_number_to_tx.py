# -*- coding: utf-8 -*-

print("1. Updating get_transaction — добавляем номер счёта...")

content = open("database.py", encoding="utf-8").read()

OLD = '''    def get_transaction(self, tid):
        with self.connect() as conn:
            r = conn.execute("""
                SELECT t.*, a.name as account_name,
                       s.full_name as seller_name
                FROM transactions t
                LEFT JOIN bank_accounts a ON t.account_id = a.id
                LEFT JOIN users s ON t.seller_id = s.id
                WHERE t.id = ?""", (tid,)).fetchone()
            return dict(r) if r else None'''

NEW = '''    def get_transaction(self, tid):
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
            return dict(r) if r else None'''

if OLD in content:
    content = content.replace(OLD, NEW)
    open("database.py", "w", encoding="utf-8").write(content)
    print("   OK: get_transaction updated")
elif "account_number as account_number" in content:
    print("   already updated")
else:
    print("   ERROR: pattern not found")


print()
print("2. Updating finance_transaction_detail.html...")

template = open("templates/finance_transaction_detail.html", encoding="utf-8").read()

# Заменяем строку "Счёт:"
OLD_LINE = '<p><b>Счёт:</b> {{ tx.account_name }}</p>'

NEW_LINE = '''<p><b>Счёт:</b> {{ tx.account_name or '—' }}</p>
      {% if tx.account_number and tx.account_number != '-' %}
      <p><b>Номер счёта:</b> <code style="background:#f8f9fa;padding:4px 10px;border-radius:6px;font-size:14px">{{ tx.account_number }}</code></p>
      {% endif %}
      {% if tx.account_bank %}
      <p><b>Банк:</b> {{ tx.account_bank }}</p>
      {% endif %}'''

if OLD_LINE in template:
    template = template.replace(OLD_LINE, NEW_LINE)
    open("templates/finance_transaction_detail.html", "w", encoding="utf-8").write(template)
    print("   OK: transaction_detail updated")
elif "Номер счёта" in template:
    print("   already updated")
else:
    print("   WARN: pattern not found, trying alternative")

    # Ищем любую строку с "Счёт:"
    import re
    pattern = r'<p><b>Счёт:</b>\s*\{\{\s*tx\.account_name\s*\}\}</p>'
    if re.search(pattern, template):
        template = re.sub(pattern, NEW_LINE, template)
        open("templates/finance_transaction_detail.html", "w", encoding="utf-8").write(template)
        print("   OK: updated via regex")


print()
print("3. Также добавим в finance_home.html и finance_transactions.html...")

# В карточках "Ожидают" в finance_home показываем номер
home = open("templates/finance_home.html", encoding="utf-8").read()
if "{{ t.account_name }}" in home and "account_number" not in home:
    # Ищем строку с "Счёт" в таблице
    home = home.replace(
        '<td>{{ t.account_name }}</td>',
        '<td>{{ t.account_name }}{% if t.account_number and t.account_number != \'-\' %}<br><small style="font-family:monospace;color:#7f8c8d">{{ t.account_number }}</small>{% endif %}</td>'
    )
    open("templates/finance_home.html", "w", encoding="utf-8").write(home)
    print("   OK: finance_home updated")

# В списке транзакций
txs = open("templates/finance_transactions.html", encoding="utf-8").read()
if "<td>{{ t.account_name }}</td>" in txs:
    txs = txs.replace(
        '<td>{{ t.account_name }}</td>',
        '<td>{{ t.account_name }}{% if t.account_number and t.account_number != \'-\' %}<br><small style="font-family:monospace;color:#7f8c8d">{{ t.account_number }}</small>{% endif %}</td>'
    )
    open("templates/finance_transactions.html", "w", encoding="utf-8").write(txs)
    print("   OK: finance_transactions updated")


print()
print("4. Проверка синтаксиса...")
import ast
try:
    ast.parse(open("database.py", encoding="utf-8").read())
    print("   database.py OK")
except SyntaxError as e:
    print("   ERROR:", e.lineno, e.msg)

print()
print("Done! Restart server.")