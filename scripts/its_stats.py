# -*- coding: utf-8 -*-
"""Статистика по сконвертированным md-страницам."""
import os

MD = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages\md"
total = with_img = with_code = with_listing = with_vrezka = empty = 0
sizes = []
for f in sorted(os.listdir(MD)):
    if not f.endswith(".md"):
        continue
    t = open(os.path.join(MD, f), encoding="utf-8").read()
    total += 1
    sizes.append((f, len(t)))
    if not t.strip():
        empty += 1
    if "![image]" in t:
        with_img += 1
    if "```" in t:
        with_code += 1
    if "Листинг" in t:
        with_listing += 1
    if "> **Подробнее**" in t:
        with_vrezka += 1

print(f"Всего md: {total}")
print(f"Пустых: {empty}")
print(f"С рисунками: {with_img}")
print(f"С кодом: {with_code}")
print(f"С листингами: {with_listing}")
print(f"С блоками Подробнее: {with_vrezka}")
print()
print("=== 10 самых маленьких (возможные проблемы) ===")
for f, s in sorted(sizes, key=lambda x: x[1])[:10]:
    print(f"  {f}: {s} chars")
print()
print("=== 5 самых больших ===")
for f, s in sorted(sizes, key=lambda x: -x[1])[:5]:
    print(f"  {f}: {s} chars")
