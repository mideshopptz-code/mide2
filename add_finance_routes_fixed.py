# -*- coding: utf-8 -*-
import re

content = open("web_app.py", encoding="utf-8").read()

if "def finance_home" in content:
    print("Routes already exist")
    exit()

ROUTES = '''

# ==================== FINANCE ====================

def accountant_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not g.user or g.user["role"] not in ("admin", "accountant"):
            flash("Доступ только для админа и бухгалтера", "error")
            return redirect("/")
        return f(*args, **kwargs)
    return wrapper


@app.route("/admin/bank-accounts", methods=["GET", "POST"])
@login_required
@admin_required
def admin_bank_accounts():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            name = request.form.get("name", "").strip()
            if name:
                db.create_bank_account(
                    name=name,
                    bank=request.form.get("bank", "").strip(),
                    account_number=request.form.get("account_number", "").strip())
                flash("Счёт добавлен", "success")
        elif action == "update":
            aid = int(request.form.get("aid"))
            db.update_bank_account(aid,
                name=request.form.get("name", "").strip(),
                bank=request.form.get("bank", "").strip(),
                account_number=request.form.get("account_number", "").strip(),
                is_active=1 if request.form.get("is_active") else 0)
            flash("Счёт обновлён", "success")
        elif action == "delete":
            aid = int(request.form.get("aid"))
            result = db.delete_bank_account(aid)
            flash("Счёт удалён" if result == "deleted" else "Счёт отключён (есть транзакции)",
                  "success")
        return redirect("/admin/bank-accounts")

    accounts = db.list_bank_accounts()
    total = db.get_total_balance()
    return render_template("admin_bank_accounts.html",
                            accounts=accounts, total=total)


@app.route("/finance")
@login_required
@accountant_required
def finance_home():
    stats = db.get_finance_stats()
    dashboard = db.get_finance_dashboard_stats(30)
    accounts = db.list_bank_accounts(active_only=True)
    pending = db.list_transactions(status="pending", limit=20)
    recent_income = db.list_transactions(status="approved", ttype="income", limit=10)
    recent_expense = db.list_transactions(status="approved", ttype="expense", limit=10)
    return render_template("finance_home.html",
                            stats=stats,
                            dashboard=dashboard,
                            accounts=accounts,
                            pending=pending,
                            recent_income=recent_income,
                            recent_expense=recent_expense,
                            is_admin=(g.user["role"] == "admin"))


@app.route("/finance/transactions")
@login_required
@accountant_required
def finance_transactions():
    ttype = request.args.get("type")
    status = request.args.get("status")
    txs = db.list_transactions(status=status, ttype=ttype, limit=300)
    return render_template("finance_transactions.html",
                            transactions=txs, current_type=ttype, current_status=status)


@app.route("/finance/transaction/<int:tid>", methods=["GET", "POST"])
@login_required
@accountant_required
def finance_transaction_detail(tid):
    tx = db.get_transaction(tid)
    if not tx:
        flash("Транзакция не найдена", "error")
        return redirect("/finance")

    if request.method == "POST":
        approve = request.form.get("approve") == "1"
        comment = request.form.get("comment", "").strip()
        if db.approve_transaction(tid, g.user["id"], approve, comment):
            flash("Одобрено" if approve else "Отклонено", "success")
        else:
            flash("Не удалось обработать", "error")
        return redirect("/finance")

    return render_template("finance_transaction_detail.html", tx=tx)


@app.route("/finance/new-expense", methods=["GET", "POST"])
@login_required
@accountant_required
def finance_new_expense():
    accounts = db.list_bank_accounts(active_only=True)

    if request.method == "POST":
        account_id = int(request.form.get("account_id"))
        amount = float(request.form.get("amount") or 0)
        comment = request.form.get("comment", "").strip()

        if not account_id or amount <= 0:
            flash("Заполните счёт и сумму", "error")
            return redirect("/finance/new-expense")

        tid = db.create_transaction(
            account_id=account_id,
            ttype="expense",
            amount=amount,
            requester_id=g.user["id"],
            comment=comment)
        flash("Заявка создана. Ждёт подтверждения бухгалтера.", "success")
        return redirect("/finance")

    return render_template("finance_new_expense.html", accounts=accounts)

'''

# Вставляем перед определением ws_connect
marker = "def ws_connect():"
idx = content.find(marker)
if idx == -1:
    print("ERROR: ws_connect not found")
    exit()

# Ищем @socketio.on("connect") выше
before_idx = content.rfind("@socketio.on", 0, idx)
if before_idx == -1:
    before_idx = idx

# Вставляем маршруты
content = content[:before_idx] + ROUTES + "\n" + content[before_idx:]

open("web_app.py", "w", encoding="utf-8").write(content)
print("OK: finance routes inserted")

# Проверка синтаксиса
import ast
try:
    ast.parse(content)
    print("SYNTAX OK!")
except SyntaxError as e:
    print("SYNTAX ERROR:", e.lineno, e.msg)

# Проверка что маршруты на месте
content2 = open("web_app.py", encoding="utf-8").read()
print()
print("Check:")
print("  finance_home:", "def finance_home" in content2)
print("  admin_bank_accounts:", "def admin_bank_accounts" in content2)
print("  finance_transactions:", "def finance_transactions" in content2)
print("  finance_transaction_detail:", "def finance_transaction_detail" in content2)
print("  finance_new_expense:", "def finance_new_expense" in content2)
print()
print("Done! Restart server.")