# -*- coding: utf-8 -*-
"""Скачивает одну страницу (pid=33) и сохраняет полный srcdoc-HTML для анализа структуры."""
import json
import sys
sys.path.insert(0, r"C:\AI_PROJECTS\QWEN_LOC\scripts")
import requests
from bs4 import BeautifulSoup

with open(r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages\_session_cookies.json", encoding="utf-8") as f:
    cookies = json.load(f)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.8078.48 Safari/537.36")
s = requests.Session()
for c in cookies:
    s.cookies.set(c["name"], c["value"], domain=c["domain"], path=c["path"])
s.headers.update({
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
})
HOME = "https://its.1c.ru/db/intgr83"

pid = 33
r = s.get(f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc", timeout=30, headers={"Referer": HOME})
soup = BeautifulSoup(r.text, "lxml")
iframe = soup.find("iframe", id="w_metadata_doc_frame")
sd = iframe.get("srcdoc")
with open(r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages\_sample_pid33.html", "w", encoding="utf-8") as f:
    f.write(sd)
print(f"pid={pid} srcdoc len={len(sd)} сохранён в _sample_pid33.html")

# Краткая структура: теги и их вложенность
inner = BeautifulSoup(sd, "lxml")
print("\n=== Топ-теги ===")
from collections import Counter
tags = Counter(t.name for t in inner.find_all(True))
for tag, cnt in tags.most_common(20):
    print(f"  <{tag}>: {cnt}")

# Заголовки
print("\n=== Заголовки ===")
for h in inner.find_all(["h1","h2","h3","h4"]):
    print(f"  {h.name}: {h.get_text(strip=True)[:70]}")

# Код-блоки
print("\n=== Код-блоки (pre/code) ===")
for i, pre in enumerate(inner.find_all("pre")[:3]):
    print(f"  pre[{i}]: {pre.get_text()[:100]!r}")
