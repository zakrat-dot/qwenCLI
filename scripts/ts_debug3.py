# -*- coding: utf-8 -*-
"""Находит диалог 'острова мидуэй' и печатает его структуру."""
import re
from bs4 import BeautifulSoup, NavigableString, Tag

SRC = r"D:\тексты для тракт\DeepSeek\googl\2-10-26\extracted\Takeout\Мои действия\Режим ИИ\МоиДействия.html"

with open(SRC, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

cells = soup.select("div.outer-cell")
print(f"Всего outer-cell: {len(cells)}")

# Ищем диалог с заголовком "острова мидуэй"
target = None
for cell in cells:
    # Проверяем заголовок (первая ссылка)
    a = cell.find("a")
    if a and "острова мидуэй" in a.get_text(strip=True).lower():
        target = cell
        break

if target is None:
    print("Не нашёл диалог 'острова мидуэй'!")
    raise SystemExit(1)

print("Нашёл диалог 'острова мидуэй'")

print("\n=== Все content-cell в этом outer-cell ===")
for cc in target.select("div.content-cell"):
    classes = cc.get("class") or []
    print(f"  classes={classes}")
    print(f"  text[:120]={cc.get_text(' ', strip=True)[:120]!r}")

print("\n=== Основной content-cell (mdl-cell--6-col, без text-right) ===")
main_cell = None
for cc in target.select("div.content-cell.mdl-cell--6-col.mdl-typography--body-1"):
    classes = cc.get("class") or []
    if "mdl-typography--text-right" not in classes:
        main_cell = cc
        break

if main_cell is None:
    print("main_cell = None!")
    raise SystemExit(1)

print(f"main_cell classes={main_cell.get('class')}")
print("\n--- Прямые дети main_cell ---")
for i, child in enumerate(main_cell.children):
    if isinstance(child, NavigableString):
        print(f"  [{i}] NavigableString: {str(child)!r}")
    elif isinstance(child, Tag):
        print(f"  [{i}] <{child.name}> classes={child.get('class')} text[:80]={child.get_text(' ', strip=True)[:80]!r}")
    else:
        print(f"  [{i}] {type(child).__name__}: {child!r}")

print("\n--- Тест regex на каждом NavigableString ---")
pat = re.compile(r"\d{1,2}\s+[а-яё]+\.\s+\d{4}\s*г")
for i, child in enumerate(main_cell.children):
    if isinstance(child, NavigableString):
        text = str(child).strip()
        m = pat.match(text)
        print(f"  [{i}] match={bool(m)} text={text[:60]!r}")

print("\n--- find_all по всему main_cell (не только прямые дети) ---")
found = False
for i, child in enumerate(main_cell.find_all(string=True)):
    text = str(child).strip()
    if text and pat.match(text):
        print(f"  НАШЁЛ: {text!r}")
        found = True
        break
if not found:
    print("  НЕ НАШЁЛ timestamp ни в одном string-узле main_cell")

# Попробуем найти timestamp где угодно в outer-cell
print("\n--- Поиск timestamp во всём outer-cell ---")
found = False
for i, child in enumerate(target.find_all(string=True)):
    text = str(child).strip()
    if text and pat.match(text):
        print(f"  НАШЁЛ в outer-cell: {text!r}")
        parent = child.parent
        print(f"  parent: <{parent.name}> classes={parent.get('class')}")
        found = True
        break
if not found:
    print("  НЕ НАШЁЛ timestamp ни в одном string-узле outer-cell")
