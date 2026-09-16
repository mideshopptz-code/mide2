# -*- coding: utf-8 -*-

content = open("templates/shop/base.html", encoding="utf-8").read()

# Удаляем все строки с повреждёнными ссылками
lines = content.split("\n")
new_lines = []
removed = 0
for line in lines:
    if '/shop/profile' in line and 'nav-link' in line:
        removed += 1
        continue
    if '/shop/logout' in line and 'nav-link' in line:
        removed += 1
        continue
    new_lines.append(line)
content = "\n".join(new_lines)
print("Removed", removed, "broken lines")

# Добавляем правильные ссылки после Бонус
old = '<a href="/shop/bonus" class="nav-link">Бонус</a>'
new = ('<a href="/shop/bonus" class="nav-link">Бонус</a>\n'
       '    <a href="/shop/profile" class="nav-link">Профиль</a>\n'
       '    <a href="/shop/logout" class="nav-link">Выйти</a>')

if old in content:
    content = content.replace(old, new)
    print("OK: profile + logout added")
else:
    print("WARN: bonus link not found, adding after Миссии")
    old2 = '<a href="/shop/missions" class="nav-link">Миссии</a>'
    if old2 in content:
        content = content.replace(old2, old2 + '\n    ' + new.split('\n')[1] + '\n    ' + new.split('\n')[2])
        print("OK: added after Missions")

open("templates/shop/base.html", "w", encoding="utf-8").write(content)

# Проверка
content2 = open("templates/shop/base.html", encoding="utf-8").read()
print()
print("Check:")
print("  /shop/profile:", '/shop/profile' in content2)
print("  /shop/logout:", '/shop/logout' in content2)
print("  Профиль:", "Профиль" in content2)
print("  Выйти:", "Выйти" in content2)