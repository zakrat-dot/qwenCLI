# -*- coding: utf-8 -*-
"""Шаг 1: проверка доступа к ITS — домашняя страница + одна контентная страница."""
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
s.headers.update({"User-Agent": UA})

print("=== ПРОВЕРКА ДОСТУПА ===")
print(f"Cookie: {len(cookies)} шт.")

# 1. Домашняя страница
r1 = s.get("https://its.1c.ru/db/intgr83", timeout=40)
print(f"\n[1] HOME  https://its.1c.ru/db/intgr83")
print(f"    HTTP {r1.status_code}  len={len(r1.content)}  ct={r1.headers.get('Content-Type')}")

# 2. Контентная страница (pid 17 — там есть картинка)
r2 = s.get("https://its.1c.ru/db/intgr83/content/17/hdoc", timeout=40)
print(f"\n[2] PAGE  https://its.1c.ru/db/intgr83/content/17/hdoc")
print(f"    HTTP {r2.status_code}  len={len(r2.content)}  ct={r2.headers.get('Content-Type')}")

# 3. Ищем iframe и подсказки по картинкам в HTML страницы
import re
html = r2.text
m = re.search(r'id="w_metadata_doc_frame"[^>]*', html)
print(f"\n[3] iframe w_metadata_doc_frame: {m.group(0)[:200] if m else 'НЕ НАЙДЕН'}")

# Есть ли <base>
b = re.search(r'<base[^>]*>', html)
print(f"[4] <base> tag: {b.group(0) if b else 'нет'}")

# Все img в полном HTML страницы (не только srcdoc)
imgs = re.findall(r'<img[^>]*src="([^"]+)"', html)
print(f"[5] img в HTML страницы: {len(imgs)}")
for u in imgs[:5]:
    print(f"    {u}")

# Ищем любые абсолютные URL картинок в HTML
abs_imgs = re.findall(r'https?://[^"\s]+?\.(?:png|jpg|jpeg|gif|webp)', html)
print(f"[6] абсолютные URL картинок: {len(abs_imgs)}")
for u in abs_imgs[:5]:
    print(f"    {u}")
