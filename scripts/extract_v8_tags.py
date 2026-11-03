"""Извлечение всех тегов {v8} из DOCX файлов в папке проекта."""

import docx
import re
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # C:\AI_PROJECTS\QWEN_LOC
results: list[dict] = []

for f in sorted(BASE.glob("*.docx")):
    try:
        doc = docx.Document(str(f))
    except Exception as e:
        print(f"⚠ {f.name} — ошибка чтения: {e}")
        continue

    tags_in_file: list[dict] = []
    full_text = "\n".join(p.text for p in doc.paragraphs) + "\n" + \
                "\n".join(
                    "".join(cell.text for cell in row.cells)
                    for table in doc.tables
                    for row in table.rows
                )

    # Ищем все {v8 ...} и {/v8 ...}
    pattern = re.compile(r"\{/?v8\s+[^}]*\}", re.IGNORECASE | re.DOTALL)
    
    for para in doc.paragraphs:
        matches = list(pattern.finditer(para.text))
        if not matches:
            # Проверяем run'ы — теги могут быть разбиты между run-ами
            runs_text = "".join(run.text for run in para.runs)
            matches = list(pattern.finditer(runs_text))
        
        for m in matches:
            tag_text = m.group(0).strip("{}")
            tags_in_file.append({
                "тег": tag_text,
                "контекст": para.text[:200],
            })

    # То же для таблиц
    for table_idx, table in enumerate(doc.tables):
        for row_idx, row in enumerate(table.rows):
            for cell in row.cells:
                matches = list(pattern.finditer(cell.text))
                if not matches:
                    runs_text = "".join(
                        run.text 
                        for p in cell.paragraphs 
                        for run in p.runs
                    )
                    matches = list(pattern.finditer(runs_text))
                
                for m in matches:
                    tag_text = m.group(0).strip("{}")
                    tags_in_file.append({
                        "тег": tag_text,
                        "контекст": f"[Таблица {table_idx+1}, строка {row_idx+1}] " + cell.text[:200],
                    })

    if tags_in_file:
        results.append({"файл": f.name, "кол_тегов": len(tags_in_file), "теги": tags_in_file})
        print(f"✅ {f.name} — найдено тегов: {len(tags_in_file)}")
    else:
        print(f"   {f.name} — тегов нет")

# Сохраняем JSON для дальнейшего использования
out = BASE / "scripts" / "v8_tags_all.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n📋 Полный результат → {out}")

# Сводка по уникальным именам тегов
all_tag_names = set()
for r in results:
    for t in r["теги"]:
        tag = t["тег"]
        # Извлекаем имя переменной из тега
        m2 = re.search(r"v8\s+(?:NAME[=]\s*)?(.+)", tag, re.IGNORECASE)
        if m2:
            all_tag_names.add(m2.group(1).strip())

print(f"\n📊 Всего уникальных имён тегов: {len(all_tag_names)}")
for name in sorted(all_tag_names):
    print(f"  · {{{name}}}")
