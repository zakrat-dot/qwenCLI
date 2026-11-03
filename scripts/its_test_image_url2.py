# -*- coding: utf-8 -*-
"""Проверяем НАЙДЕННЫЙ паттерн картинок: /db/content/intgr83/src/<file>"""
import json
import requests

BASE = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages"
COOKIES = BASE + r"\_session_cookies.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.8078.48 Safari/537.36")

with open(COOKIES, encoding="utf-8") as f:
    cookies = json.load(f)

s = requests.Session()
for c in cookies:
    s.cookies.set(c["name"], c["value"], domain=c["domain"], path=c["path"])
s.headers.update({"User-Agent": UA, "Referer": "https://its.1c.ru/db/intgr83"})

# Прогрев
s.get("https://its.1c.ru/db/intgr83", timeout=40)

test = "01_02.png"
tok = "0000153266FEEB6F-v2"
candidates = [
    f"https://its.1c.ru/db/content/intgr83/src/{test}?_={tok}",
    f"https://its.1c.ru/db/content/intgr83/src/{test}",
]
for url in candidates:
    try:
        r = s.get(url, timeout=40)
        ct = r.headers.get("Content-Type", "?")
        print(f"HTTP {r.status_code}  len={len(r.content):>8}  ct={ct:<25}  {url}")
        if r.status_code == 200 and len(r.content) > 100:
            # Сохраняем тестовую картинку
            out = BASE + r"\_test_img.png"
            with open(out, "wb") as f:
                f.write(r.content)
            print(f"  -> СОХРАНЕНО {out} ({len(r.content)} bytes)")
            break
    except Exception as e:
        print(f"ERROR {url}: {e}")
