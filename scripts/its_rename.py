# -*- coding: utf-8 -*-
"""Переименовывает NNN.md -> 'NNN. Название.md' в папке Obsidian
и пересобирает TOC.md со ссылками на новые имена файлов.

Номер-префикс (NNN.) сохраняется, чтобы:
  - файлы оставались в правильном порядке в проводнике Obsidian;
  - не было коллизий у повторяющихся заголовков
    (например «Общая информация» на стр. 7, 29, 48, 72, 93, 100, 182, 239).
"""
import json
import os
import re

BASE = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages"
OBS = r"C:\Voult\Volt\1c\Книги1сИтс\Технологии интеграции"

with open(os.path.join(BASE, "_id2title.json"), encoding="utf-8") as f:
    id2title = json.load(f)

# Запрещённые в именах файлов символы Windows
ILLEGAL = r'[<>:"/\\|?*\x00-\x1f]'

def sanitize(title: str) -> str:
    t = re.sub(ILLEGAL, " ", title)
    t = re.sub(r"\s+", " ", t).strip()
    # убираем пробелы у краёв и точку в конце
    t = t.strip().rstrip(".")
    return t

def fname(pid: int, title: str) -> str:
    return f"{pid:03d}. {sanitize(title)}.md"

# --- 1. Переименование файлов ---
renamed = 0
skipped = 0
errors = []
for pid_str, title in id2title.items():
    if pid_str == "999999":
        continue
    pid = int(pid_str)
    src = os.path.join(OBS, f"{pid:03d}.md")
    dst = os.path.join(OBS, fname(pid, title))
    if not os.path.exists(src):
        skipped += 1
        continue
    if src == dst:
        continue
    if os.path.exists(dst):
        # уже переименован ранее — пропускаем
        skipped += 1
        continue
    try:
        os.rename(src, dst)
        renamed += 1
    except Exception as e:
        errors.append(f"{src} -> {dst}: {e}")

print(f"Переименовано: {renamed}")
print(f"Пропущено: {skipped}")
if errors:
    print("Ошибки:")
    for e in errors:
        print("  " + e)

# --- 2. Пересборка TOC.md ---
pages = []
for pid_str, title in id2title.items():
    if pid_str == "999999":
        continue
    pages.append((int(pid_str), title))
pages.sort(key=lambda x: x[0])

chapters = []
front = []
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
    fn = fname(pid, title)
    if os.path.exists(os.path.join(OBS, fn)):
        return f"[{title}]({fn})"
    return f"{title} *(нет файла)*"

lines = []
lines.append("# Технологии интеграции 1С:Предприятия 8.3")
lines.append("")
lines.append("Полный текст книги (257 страниц), скачанный с its.1c.ru и сконвертированный в Markdown.")
lines.append("")
lines.append(f"Всего страниц: {len(pages)}")
lines.append("")

if front:
    lines.append("## Предварительные страницы")
    lines.append("")
    for pid, title in front:
        lines.append(f"- {md_link(pid, title)}")
    lines.append("")

for chap_title, chap_pages in chapters:
    lines.append(f"## {chap_title}")
    lines.append("")
    for pid, title in chap_pages:
        lines.append(f"- {md_link(pid, title)}")
    lines.append("")

lines.append("---")
lines.append("")
lines.append("## Структура файлов")
lines.append("")
lines.append("- `NNN. Название.md` — текст страницы (NNN — номер страницы, Название — её заголовок)")
lines.append("- `TOC.md` — это оглавление со ссылками на все страницы")
lines.append("")

toc_path = os.path.join(OBS, "TOC.md")
with open(toc_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"TOC.md пересобран: {toc_path}")
print(f"  Фронт-страниц: {len(front)}")
print(f"  Глав: {len(chapters)}")
for ct, cp in chapters:
    print(f"    - {ct}: {len(cp)} стр.")
print(f"  Всего страниц: {len(pages)}")
