# -*- coding: utf-8 -*-
"""Печатает структуру content-элементов ответа Gemini для 'острова мидуэй'."""
import sys
sys.path.insert(0, r"C:\AI_PROJECTS\QWEN_LOC\scripts")
from bs4 import BeautifulSoup, NavigableString, Tag
from gemini_to_md import (
    DEFAULT_SRC, extract_timestamp, extract_title, parse_content_cell,
)

with open(DEFAULT_SRC, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

cells = soup.select("div.outer-cell")
target = None
for cell in cells:
    a = cell.find("a")
    if a and "острова мидуэй" in a.get_text(strip=True).lower():
        target = cell
        break

if target is None:
    print("Не нашёл!")
    raise SystemExit(1)

main_cell = None
for cc in target.select("div.content-cell.mdl-cell--6-col.mdl-typography--body-1"):
    if "mdl-typography--text-right" not in (cc.get("class") or []):
        main_cell = cc
        break

segments = parse_content_cell(main_cell, None, None)
print(f"Сегментов: {len(segments)}")
for si, (role, content) in enumerate(segments):
    print(f"\n=== Сегмент {si}: role={role}, элементов={len(content)} ===")
    for i, c in enumerate(content):
        if isinstance(c, NavigableString):
            print(f"  [{i}] NavigableString: {str(c)[:80]!r}")
        elif isinstance(c, Tag):
            print(f"  [{i}] <{c.name}> classes={c.get('class')} text[:60]={c.get_text(' ', strip=True)[:60]!r}")
        else:
            print(f"  [{i}] {type(c).__name__}: {c!r}")
