# -*- coding: utf-8 -*-
"""Разведка структуры МоиДействия.html (Режим ИИ)."""
import re
from bs4 import BeautifulSoup

HTML = r"D:\тексты для тракт\DeepSeek\googl\2-10-26\extracted\Takeout\Мои действия\Режим ИИ\МоиДействия.html"

with open(HTML, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

cells = soup.select("div.outer-cell")
print("Всего outer-cell:", len(cells))
print("=" * 70)

# Берём несколько записей разных типов и печатаем их "скелет"
def skeleton(cell, depth=0, max_depth=4):
    out = []
    for child in cell.children:
        if getattr(child, "name", None) is None:
            t = str(child).strip()
            if t:
                out.append("  " * depth + "TEXT: " + t[:80].replace("\n", " "))
            continue
        attrs = " ".join(f'{k}={v!r}' for k, v in child.attrs.items() if k in ("class", "href"))
        out.append("  " * depth + f"<{child.name}> {attrs}")
        if depth < max_depth:
            out.extend(skeleton(child, depth + 1, max_depth))
    return out

# Печатаем 3 первые записи, где есть "Ваш запрос"
shown = 0
for i, cell in enumerate(cells):
    txt = cell.get_text(" ", strip=True)
    if "Ваш запрос" in txt and shown < 2:
        print(f"\n### ЗАПИСЬ #{i} (с ответом) ###")
        for line in skeleton(cell, max_depth=3):
            print(line)
        shown += 1

# Одна запись "Использовано приложение"
for i, cell in enumerate(cells):
    txt = cell.get_text(" ", strip=True)
    if "Использовано приложение" in txt:
        print(f"\n### ЗАПИСЬ #{i} (Использовано приложение) ###")
        for line in skeleton(cell, max_depth=3):
            print(line)
        break

# Одна запись "Объектива"
for i, cell in enumerate(cells):
    txt = cell.get_text(" ", strip=True)
    if "Объектива" in txt:
        print(f"\n### ЗАПИСЬ #{i} (Объектив) ###")
        for line in skeleton(cell, max_depth=3):
            print(line)
        break
