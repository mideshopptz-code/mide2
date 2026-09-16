# -*- coding: utf-8 -*-

content = open("templates/staff_form.html", encoding="utf-8").read()

print("accountant already:", "accountant" in content)
print()

# Ищем строку с seller
old = '<option value="seller"'
if old in content:
    # Находим конец этой строки
    idx = content.find(old)
    end = content.find("</option>", idx) + len("</option>")
    
    # Добавляем бухгалтера после seller
    accountant = '\n        <option value="accountant" {% if user and user.role == \'accountant\' %}selected{% endif %}>💼 Бухгалтер</option>'
    content = content[:end] + accountant + content[end:]
    
    open("templates/staff_form.html", "w", encoding="utf-8").write(content)
    print("OK: accountant added to staff_form.html")
    print("Now reload the page in browser")
else:
    print("ERROR: seller option not found")

# Также добавляем в web_app.py чтобы можно было создавать
web = open("web_app.py", encoding="utf-8").read()
old_check = 'if role not in ("senior_seller", "mentor", "seller"):'
new_check = 'if role not in ("senior_seller", "mentor", "seller", "accountant"):'
if old_check in web:
    web = web.replace(old_check, new_check)
    open("web_app.py", "w", encoding="utf-8").write(web)
    print("OK: web_app.py allows accountant")
else:
    print("web_app.py: pattern not found (may already be updated)")

print()
print("Done!")
print("Restart server and try again.")