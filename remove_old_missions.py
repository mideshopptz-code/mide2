# -*- coding: utf-8 -*-

content = open("web_app.py", encoding="utf-8").read()

# Удаляем СТАРЫЙ маршрут: с 883 строки (def customer_missions) до 895 (перед def uploaded_file)
# Находим точно по тексту

# Старый маршрут выглядит так:
# @app.route("/shop/missions")
# @customer_required
# def customer_missions():
#     missions = db.get_customer_all_missions(g.customer["id"])
#     return render_template('shop/missions.html', missions=missions)
#
# И следующий:
# @app.route("/shop/missions/<int:mid>/claim", methods=["POST"])
# @customer_required
# def mission_claim(mid):
#     ...

# Удаляем блок от "@app.route("/shop/missions")" до "@app.route("/uploads/" 
# (uploaded_file идёт сразу после mission_claim)

marker_start = '@app.route("/shop/missions")\n@customer_required\ndef customer_missions():'
marker_end = '@app.route("/uploads/'

idx_start = content.find(marker_start)
idx_end = content.find(marker_end)

if idx_start == -1:
    print("ERROR: old customer_missions block not found")
elif idx_end == -1:
    print("ERROR: uploaded_file marker not found")
else:
    # Удаляем весь блок между ними
    removed = content[idx_start:idx_end]
    content = content[:idx_start] + content[idx_end:]
    print("Removed block, length:", len(removed))
    print("First 200 chars of removed:")
    print(removed[:200])
    print()

    # Сохраняем
    open("web_app.py", "w", encoding="utf-8").write(content)

    # Проверяем
    print("After removal:")
    print("  customer_missions:", content.count("def customer_missions"))
    print("  mission_claim:", content.count("def mission_claim"))
    print("  shop_missions:", content.count("def shop_missions"))
    print("  shop_mission_complete:", content.count("def shop_mission_complete"))

    # Проверяем синтаксис
    import ast
    try:
        ast.parse(content)
        print()
        print("SYNTAX OK!")
    except SyntaxError as e:
        print()
        print("SYNTAX ERROR at line", e.lineno, ":", e.msg)

print()
print("Done! Restart server.")