# -*- coding: utf-8 -*-
"""Проверяет, доступен ли контент страницы через src-URL iframe
(/db/content/intgr83/src/N.html) — возможно, это и есть реальный контент."""
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

# pid=93 -> src=/db/content/intgr83/src/89.html
# pid=33 -> src=/db/content/intgr83/src/29.html
# pid=5  -> src=/db/content/intgr83/src/1.html
tests = [
    (93, "https://its.1c.ru/db/content/intgr83/src/89.html"),
    (33, "https://its.1c.ru/db/content/intgr83/src/29.html"),
    (5,  "https://its.1c.ru/db/content/intgr83/src/1.html"),
]
for pid, url in tests:
    r = s.get(url, timeout=30, headers={"Referer": "https://its.1c.ru/db/intgr83"})
    soup = BeautifulSoup(r.text, "lxml")
    # Ищем основной контент
    body = soup.find("body")
    text_len = len(body.get_text(strip=True)) if body else 0
    # Ищем заголовок
    h = soup.find(["h1", "h2", "title"])
    title = h.get_text(strip=True) if h else "(нет)"
    print(f"pid={pid}: HTTP {r.status_code} len={len(r.text)} text_len={text_len}")
    print(f"   title: {title[:80]}")
    print(f"   first 200 chars: {body.get_text(' ', strip=True)[:200] if body else '(нет body)'}")
    print()
