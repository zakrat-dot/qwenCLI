# -*- coding: utf-8 -*-
"""Собирает оглавление TOC.md из _id2title.json.
Страницы группируются по главам (маркер «Глава N ...»).
Каждая страница — ссылка на свой md-файл.
"""
import json
import os
import re

BASE = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages"
MD = os.path.join(BASE, "md")
TOC = os.path.join(BASE, "TOC.md")

with open(os.path.join(BASE, "_id2title.json"), encoding="utf-8") as f:
    id2title = json.load(f)

# Собираем страницы по возрастанию pid (исключаем служебный 999999)
pages = []
for pid_str, title in id2title.items():
    if pid_str == "999999":
        continue
    pid = int(pid_str)
    pages.append((pid, title))
pages.sort(key=lambda x: x[0])

# Определяем границы глав: страницы, чей заголовок начинается с «Глава»
chapters = []  # список (chapter_title, [ (pid, title), ... ])
front = []     # страницы до первой главы
current = None
for pid, title in pages:
    if re.match(r"^Глава\s+\d", title):
        current = (title, [])
        chapters.append(current)
    elif current is None:
        front.append((pid, title))
    else:
        current[1].append((pid, title))

def md_link(pid, title):
    fname = f"{pid:03d}.md"
    path = os.path.join(MD, fname)
    exists = os.path.exists(path)
    if exists:
        return f"[{title}]({fname})"
    return f"{title} *(нет файла)*"

lines = []
lines.append("# Технологии интеграции 1С:Предприятия 8.3")
lines.append("")
lines.append("Полный текст книги (257 страниц), скачанный с its.1c.ru и сконвертированный в Markdown.")
lines.append("")
lines.append(f"Всего страниц: {len(pages)}")
lines.append("")

# Фронт-материалы
if front:
    lines.append("## Предварительные страницы")
    lines.append("")
    for pid, title in front:
        lines.append(f"- {md_link(pid, title)}")
    lines.append("")

# Главы
for chap_title, chap_pages in chapters:
    lines.append(f"## {chap_title}")
    lines.append("")
    for pid, title in chap_pages:
        lines.append(f"- {md_link(pid, title)}")
    lines.append("")

# Служебная информация
lines.append("---")
lines.append("")
lines.append("## Структура файлов")
lines.append("")
lines.append("- `md/NNN.md` — текст страницы NNN (3 цифры)")
lines.append("- `raw/NNN.html` — исходный HTML страницы (srcdoc из iframe)")
lines.append("- `_id2title.json` — соответствие pid → заголовок")
lines.append("- `_download_summary.json` — статус скачивания каждой страницы")
lines.append("")

with open(TOC, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"TOC.md создан: {TOC}")
print(f"  Фронт-страниц: {len(front)}")
print(f"  Глав: {len(chapters)}")
for ct, cp in chapters:
    print(f"    - {ct}: {len(cp)} стр.")
print(f"  Всего страниц: {len(pages)}")
