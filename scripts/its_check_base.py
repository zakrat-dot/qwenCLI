# -*- coding: utf-8 -*-
"""Проверяем, что <base> одинаков на разных страницах + берём реальные img src."""
import json
import re
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
s.get("https://its.1c.ru/db/intgr83", timeout=40)

for pid in [1, 50, 100, 200, 257]:
    r = s.get(f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc", timeout=40)
    html = r.text
    b = re.search(r'<base[^>]*href="([^"]+)"', html)
    base_href = b.group(1) if b else "НЕТ"
    # img src из srcdoc (unescape)
    import html as htmlmod
    doc = htmlmod.unescape(html)
    imgs = re.findall(r'<img[^>]*src="([^"]+)"', doc)
    print(f"pid={pid}  HTTP {r.status_code}  base={base_href}")
    for u in imgs[:3]:
        print(f"    img: {u}")
