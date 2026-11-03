"""Простой список уникальных тегов v8 в Excel."""

import json
from pathlib import Path
try:
    from openpyxl import Workbook
except ImportError:
    print("⚠ pip install openpyxl")
    raise SystemExit(1)

BASE = Path(__file__).resolve().parent.parent
with open(BASE / "scripts" / "v8_tags_all.json", encoding="utf-8") as f:
    data = json.load(f)

# Собираем уникальные имена тегов (без префикса v8, без слэша)
names: set[str] = set()
for entry in data:
    for t in entry["теги"]:
        raw = t["тег"].strip().lstrip("/")
        name_part = raw.replace("v8", "", 1).strip()
        names.add(name_part)

wb = Workbook()
ws = wb.active
ws.title = "Теги v8"

# Заголовки
for col, h in enumerate(["№", "Имя тега"], 1):
    c = ws.cell(row=1, column=col, value=h)
    from openpyxl.styles import Font
    c.font = Font(bold=True)

# Данные
for idx, name in enumerate(sorted(names), 1):
    ws.cell(row=idx + 1, column=1, value=idx)
    ws.cell(row=idx + 1, column=2, value=name)

ws.column_dimensions["A"].width = 5
ws.column_dimensions["B"].width = 48

out_path = BASE / "теги_v8_список.xlsx"
wb.save(out_path)
print(f"✅ {out_path} — {len(names)} тегов")
