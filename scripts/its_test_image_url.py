# -*- coding: utf-8 -*-
"""Тестирует разные URL-паттерны для картинок ITS."""
import requests
import json

COOKIES = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages\_session_cookies.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.8078.48 Safari/537.36"

with open(COOKIES, encoding="utf-8") as f:
    cookies = json.load(f)

s = requests.Session()
for c in cookies:
    s.cookies.set(c["name"], c["value"], domain=c["domain"], path=c["path"])
s.headers.update({"User-Agent": UA, "Referer": "https://its.1c.ru/db/intgr83"})

# Прогрев
r0 = s.get("https://its.1c.ru/db/intgr83", timeout=40)
print(f"HOME HTTP {r0.status_code}")

# Тестируем разные URL-паттерны для одной картинки
test_image = "01_02.png"
pid = 17
patterns = [
    f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc/{test_image}",
    f"https://its.1c.ru/db/intgr83/content/{pid}/{test_image}",
    f"https://its.1c.ru/db/intgr83/{test_image}",
    f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc/{test_image}?_=0000153266FEEB6F-v2",
    f"https://its.1c.ru/db/intgr83/content/{pid}/{test_image}?_=0000153266FEEB6F-v2",
    f"https://its.1c.ru/db/intgr83/{test_image}?_=0000153266FEEB6F-v2",
    f"https://its.1c.ru/db/intgr83/files/{test_image}",
    f"https://its.1c.ru/images/{test_image}",
    f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc/img/{test_image}",
]

for url in patterns:
    try:
        r = s.get(url, timeout=40)
        ct = r.headers.get("Content-Type", "?")
        print(f"HTTP {r.status_code} len={len(r.content):>8} ct={ct:<30} {url}")
    except Exception as e:
        print(f"ERROR {url}: {e}")
