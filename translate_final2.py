# -*- coding: utf-8 -*-
import os
import re

print("=" * 60)
print("ФИНАЛЬНЫЙ ПЕРЕВОД v2")
print("=" * 60)
print()

REPLACEMENTS = [
    ("Actual", "Факт"),
    ("Expected", "Ожидается"),
    ("Diff", "Расхождение"),
    ("Results", "Результаты"),
    ("Revenue", "Выручка"),
    ("Subtotal", "Итого"),
    ("District", "Район"),
    ("Registration", "Регистрация"),
]


def process_file(path):
    try:
        content = open(path, encoding="utf-8").read()
    except Exception:
        return 0
    
    original = content
    count = 0
    
    for old, new in REPLACEMENTS:
        # Заменяем только между тегами >X<
        pattern = r'>' + re.escape(old) + r'<'
        if re.search(pattern, content):
            content = re.sub(pattern, '>' + new + '<', content)
            count += 1
        
        # И в placeholder
        pattern2 = r'placeholder="' + re.escape(old) + r'"'
        if re.search(pattern2, content):
            content = re.sub(pattern2, 'placeholder="' + new + '"', content)
            count += 1
        
        # В value
        pattern3 = r'value="' + re.escape(old) + r'"'
        if re.search(pattern3, content):
            content = re.sub(pattern3, 'value="' + new + '"', content)
            count += 1
        
        # В title, label
        pattern4 = r'>' + re.escape(old) + r'\s'
        if re.search(pattern4, content):
            content = re.sub(pattern4, '>' + new + ' ', content)
            count += 1
    
    if content != original:
        open(path, "w", encoding="utf-8").write(content)
        return count
    return 0


total = 0
files = 0

for folder in ["templates", "templates/shop"]:
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if fname.endswith(".html"):
            path = os.path.join(folder, fname)
            cnt = process_file(path)
            if cnt > 0:
                files += 1
                total += cnt
                print("  OK", path, "(" + str(cnt) + ")")

print()
print("Файлов:", files, "| Замен:", total)
print()

# Проверка
print("Проверка...")
english_pattern = re.compile(r'>([A-Z][a-z]+(?:\s+[A-Za-z]+)*)<')
found = {}

for folder in ["templates", "templates/shop"]:
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if not fname.endswith(".html"):
            continue
        try:
            content = open(os.path.join(folder, fname), encoding="utf-8").read()
        except Exception:
            continue
        
        for m in english_pattern.finditer(content):
            text = m.group(1)
            if re.search(r'[а-яА-ЯёЁ]', text):
                continue
            if '{{' in text or '{%' in text:
                continue
            if text in ['OK', 'ID', 'KPI', 'MIDE', 'Telegram', 'Instagram', 'YouTube', 'VK', 'TikTok', 'RUB']:
                continue
            found.setdefault(text, []).append(fname)

if found:
    print("Осталось:")
    for text in sorted(found.keys()):
        print("  '" + text + "' →", ", ".join(set(found[text])))
else:
    print("✓ ВСЁ ПО-РУССКИ!")

print()
print("Restart server + Ctrl+F5")