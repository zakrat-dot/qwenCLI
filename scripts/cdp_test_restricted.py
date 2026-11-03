# -*- coding: utf-8 -*-
"""Извлекает куки сессии из CDP-браузера и тестирует доступ к ранее
заблокированной странице (pid=93) через requests с этими куками."""
import json
import sys
sys.path.insert(0, r"C:\AI_PROJECTS\QWEN_LOC\scripts")
from cdp_client import find_page_tab, CDP
import requests
from bs4 import BeautifulSoup

tab = find_page_tab("its.1c.ru") or find_page_tab()
cdp = CDP(tab)
cookies = cdp.get_cookies()
cdp.close()

# Сохраняем куки в файл для переиспользования
out = []
for c in cookies:
    out.append({
        "name": c["name"],
        "value": c["value"],
        "domain": c.get("domain", ""),
        "path": c.get("path", "/"),
    })
with open(r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages\_session_cookies.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"Сохранено куки: {len(out)} шт.")

# Собираем сессию requests
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.8078.48 Safari/537.36")
s = requests.Session()
for c in out:
    s.cookies.set(c["name"], c["value"], domain=c["domain"], path=c["path"])
s.headers.update({
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
})

def classify(r):
    soup = BeautifulSoup(r.text, "lxml")
    iframe = soup.find("iframe", id="w_metadata_doc_frame")
    if not iframe:
        return f"iframe НЕТ (HTTP {r.status_code})"
    if iframe.get("srcdoc"):
        return f"ДОСТУПНО (srcdoc len={len(iframe['srcdoc'])})"
    src = iframe.get("src")
    if src:
        return f"ОГРАНИЧЕНО (src={src})"
    return "ни srcdoc, ни src"

HOME = "https://its.1c.ru/db/intgr83"
print("\n=== Тест ранее заблокированных страниц (pid=93, 33, 5) ===")
for pid in [93, 33, 5]:
    url = f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc"
    r = s.get(url, timeout=30, headers={"Referer": HOME})
    print(f"  pid={pid}: {classify(r)}")
