"""Выгрузка всех тегов {v8} в Excel — сводная таблица по документам."""

import json
from pathlib import Path
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
except ImportError:
    print("⚠ Установи openpyxl: pip install openpyxl")
    raise SystemExit(1)

BASE = Path(__file__).resolve().parent.parent
json_path = BASE / "scripts" / "v8_tags_all.json"

with open(json_path, encoding="utf-8") as f:
    data = json.load(f)

wb = Workbook()
ws = wb.active
ws.title = "Теги v8 по документам"

# --- Стили ---
hdr_font  = Font(bold=True, color="FFFFFF", size=11)
hdr_fill  = PatternFill("solid", fgColor="2F5496")
ctx_align = Alignment(wrap_text=True, vertical="top")
cell_border = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"))

# Цвета для типов тегов
fill_open   = PatternFill("solid", fgColor="C6EFCE")  # зелёный — открывающий/переменная
fill_close  = PatternFill("solid", fgColor="FCD5B4")  # оранжевый — закрывающий
fill_region = PatternFill("solid", fgColor="D9E2F3")  # синий — область

# --- Заголовки ---
headers = [
    ("А", 10),   # №
    ("Б", 45),   # Документ
    ("В", 8),    # Тег (встреча)
    ("Г", 32),   # Имя тега
    ("Д", 16),   # Тип
    ("Е", 70),   # Расположение
    ("Ж", 90),   # Контекст в документе
]

for col_idx, (letter, width) in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_idx, value=letter if col_idx > 2 else letter)
    cell.font = hdr_font
    cell.fill = hdr_fill
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = cell_border

# Правильные заголовки
real_headers = ["№", "Документ", "Тег (встреча)", "Имя тега", "Тип", "Расположение", "Контекст в документе"]
for col_idx, h in enumerate(real_headers, 1):
    ws.cell(row=1, column=col_idx, value=h)

# --- Данные ---
row = 2
counter = 0
file_stats: dict[str, int] = {}

for entry in data:
    fname = entry["файл"]
    file_stats[fname] = len(entry["теги"])
    
    for idx, tag_info in enumerate(entry["теги"], 1):
        counter += 1
        raw_tag = tag_info["тег"].strip()
        
        # Определяем тип и имя тега
        if raw_tag.startswith("/"):
            typ = "Закрывающий"
            fill = fill_close
            name_part = raw_tag[1:].strip()
        elif "Область" in raw_tag:
            typ = "Область (блок)"
            fill = fill_region
            name_part = raw_tag.replace("v8", "").replace("/", "").strip()
        else:
            typ = "Переменная"
            fill = fill_open
            name_part = raw_tag.replace("v8", "", 1).strip()
        
        # Расположение (таблица или параграф)
        ctx = tag_info["контекст"]
        if ctx.startswith("[Таблица"):
            location = ctx.split("]")[0] + "]"
        else:
            location = "Параграф"
        
        values = [counter, fname, idx, name_part, typ, location, ctx[:500]]
        for col_idx, val in enumerate(values, 1):
            cell = ws.cell(row=row, column=col_idx, value=val)
            if col_idx == 5:  # Тип — цветная ячейка
                cell.fill = fill
            if col_idx == 7:  # Контекст — перенос строк
                cell.alignment = ctx_align
            cell.border = cell_border
        
        row += 1

# --- Ширина колонок ---
col_widths = [6, 50, 12, 40, 18, 22, 95]
from openpyxl.utils import get_column_letter
for col_idx, w in enumerate(col_widths, 1):
    ws.column_dimensions[get_column_letter(col_idx)].width = w

# Фиксированная высота строк
ws.auto_filter.ref = ws.dimensions
ws.freeze_panes = "B2"

# --- Вкладка сводка ---
ws2 = wb.create_sheet("Сводка")
sw_headers = ["Документ", "Всего тегов", "Уникальные имена"]
for col_idx, h in enumerate(sw_headers, 1):
    cell = ws2.cell(row=1, column=col_idx, value=h)
    cell.font = hdr_font
    cell.fill = hdr_fill

# Собираем уникальные имена по файлам
sw_row = 2
for entry in data:
    names = set()
    for t in entry["теги"]:
        raw = t["тег"].strip().lstrip("/")
        name_part = raw.replace("v8", "", 1).strip()
        names.add(name_part)
    
    ws2.cell(row=sw_row, column=1, value=entry["файл"])
    ws2.cell(row=sw_row, column=2, value=file_stats[entry["файл"]])
    ws2.cell(row=sw_row, column=3, value="; ".join(sorted(names)))
    sw_row += 1

ws2.column_dimensions["A"].width = 50
ws2.column_dimensions["B"].width = 14
ws2.column_dimensions["C"].width = 80

# --- Сохранение ---
out_path = BASE / "теги_v8_по_документам.xlsx"
wb.save(out_path)
print(f"✅ Сохранено → {out_path}")
print(f"   Всего записей: {counter}, файлов: {len(data)}")
