# -*- coding: utf-8 -*-
"""Соответствие доступных id страниц их заголовкам из оглавления."""
import re
import json
from bs4 import BeautifulSoup

HOME = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_intgr83_home.html"
html = open(HOME, encoding="utf-8").read()
soup = BeautifulSoup(html, "lxml")

# Собираем id -> заголовок из дерева оглавления (li id="toc_N")
id2title = {}
for li in soup.find_all("li", id=re.compile(r"^toc_\d+$")):
    tid = int(li["id"].split("_")[1])
    a = li.find("a", href=re.compile(r"/db/intgr83/content/\d+/hdoc"))
    if a:
        title = a.get_text(strip=True)
        id2title[tid] = title

summary = json.load(open(r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages\_scan_summary.json", encoding="utf-8"))
accessible = summary["accessible"]

print(f"Доступных страниц: {len(accessible)}\n")
for pid in accessible:
    t = id2title.get(pid, "(нет в оглавлении)")
    print(f"  {pid:>4}  {t}")

# Сохраним маппинг для дальнейшего использования
with open(r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages\_id2title.json", "w", encoding="utf-8") as f:
    json.dump({str(k): v for k, v in id2title.items()}, f, ensure_ascii=False, indent=2)
print("\n[OK] маппинг id->заголовок сохранён")
