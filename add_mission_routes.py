# -*- coding: utf-8 -*-

ROUTES = '''

# ==================== MISSIONS CONSTRUCTOR ====================

@app.route("/missions")
@login_required
@admin_required
def admin_missions_list():
    missions = db.list_missions_admin()
    pending = db.get_pending_missions()
    return render_template("admin_missions.html",
                            missions=missions, pending=pending)


@app.route("/missions/new", methods=["GET", "POST"])
@login_required
@admin_required
def admin_mission_create():
    if request.method == "POST":
        code = request.form.get("code", "").strip().lower().replace(" ", "_")
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        icon = request.form.get("icon", "🎯").strip() or "🎯"
        category = request.form.get("mission_category", "buy")
        target = int(request.form.get("target_value") or 1)
        reward = int(request.form.get("reward_value") or 0)
        action_url = request.form.get("action_url", "").strip()
        platform = request.form.get("platform", "").strip()
        verify_hint = request.form.get("verify_hint", "").strip()
        repeat = request.form.get("repeat_type", "once")
        requires_approval = 1 if request.form.get("requires_approval") else 0

        if not code or not title or reward <= 0:
            flash("Заполните код, название и награду", "error")
            return redirect("/missions/new")

        # Проверяем уникальность кода
        existing = db.get_mission_by_code(code)
        if existing:
            code = code + "_" + str(int(__import__("time").time()))

        mid = db.create_mission_full(
            code=code, title=title, description=description, icon=icon,
            mission_category=category, target_value=target,
            reward_value=reward, action_url=action_url, platform=platform,
            verify_hint=verify_hint, repeat_type=repeat,
            requires_approval=requires_approval)

        flash("Миссия создана!", "success")
        return redirect("/missions")

    return render_template("admin_mission_form.html", mission=None)


@app.route("/missions/<int:mid>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def admin_mission_edit(mid):
    m = db.get_mission(mid)
    if not m:
        flash("Миссия не найдена", "error")
        return redirect("/missions")

    if request.method == "POST":
        with db.connect() as conn:
            conn.execute("""UPDATE missions SET
                title=?, description=?, icon=?, mission_category=?,
                target_value=?, reward_value=?, action_url=?, platform=?,
                verify_hint=?, repeat_type=?, requires_approval=?
                WHERE id=?""",
                (request.form.get("title", "").strip(),
                 request.form.get("description", "").strip(),
                 request.form.get("icon", "🎯").strip() or "🎯",
                 request.form.get("mission_category", "buy"),
                 int(request.form.get("target_value") or 1),
                 int(request.form.get("reward_value") or 0),
                 request.form.get("action_url", "").strip(),
                 request.form.get("platform", "").strip(),
                 request.form.get("verify_hint", "").strip(),
                 request.form.get("repeat_type", "once"),
                 1 if request.form.get("requires_approval") else 0,
                 mid))
        flash("Миссия обновлена", "success")
        return redirect("/missions")

    return render_template("admin_mission_form.html", mission=m)


@app.route("/missions/<int:mid>/delete", methods=["POST"])
@login_required
@admin_required
def admin_mission_delete(mid):
    with db.connect() as conn:
        conn.execute("DELETE FROM missions WHERE id=?", (mid,))
        conn.execute("DELETE FROM customer_mission_progress WHERE mission_id=?", (mid,))
    flash("Миссия удалена", "success")
    return redirect("/missions")


@app.route("/missions/<int:mid>/toggle", methods=["POST"])
@login_required
@admin_required
def admin_mission_toggle(mid):
    with db.connect() as conn:
        conn.execute("UPDATE missions SET is_active = 1 - is_active WHERE id=?", (mid,))
    flash("Статус изменён", "success")
    return redirect("/missions")


@app.route("/missions/approve/<int:progress_id>", methods=["POST"])
@login_required
@admin_required
def admin_mission_approve(progress_id):
    approve = request.form.get("approve") == "1"
    db.approve_mission_customer(progress_id, approve)
    flash("Одобрено" if approve else "Отклонено", "success")
    return redirect("/missions")


# ==================== MISSIONS FOR CUSTOMERS ====================

@app.route("/shop/missions")
@customer_required
def shop_missions():
    missions = db.get_customer_all_missions(g.customer["id"])
    return render_template("shop/missions.html", missions=missions)


@app.route("/shop/missions/<int:mid>/start", methods=["POST"])
@customer_required
def shop_mission_start(mid):
    db.start_mission(g.customer["id"], mid)
    flash("Миссия начата!", "success")
    return redirect("/shop/missions")


@app.route("/shop/missions/<int:mid>/complete", methods=["POST"])
@customer_required
def shop_mission_complete(mid):
    proof_text = request.form.get("proof_text", "").strip()
    proof_url = request.form.get("proof_url", "").strip()
    db.complete_mission_customer(g.customer["id"], mid, proof_text, proof_url)
    flash("Отправлено на проверку! Ожидайте подтверждения.", "success")
    return redirect("/shop/missions")
'''

content = open("web_app.py", encoding="utf-8").read()

if "admin_missions_list" not in content:
    # Ищем маркер перед WEBSOCKET
    marker = "# ================= WEBSOCKET ================="
    if marker in content:
        content = content.replace(marker, ROUTES + "\n" + marker)
        open("web_app.py", "w", encoding="utf-8").write(content)
        print("OK: mission routes added to web_app.py")
    else:
        print("ERROR: marker not found")
else:
    print("routes already added")