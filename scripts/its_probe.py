# -*- coding: utf-8 -*-
"""Разведка: какие библиотеки есть + структура контентной страницы content/47."""
import importlib

for mod in ["bs4", "html2text", "markdownify", "lxml", "requests"]:
    try:
        m = importlib.import_module(mod)
        print(f"[OK] {mod} {getattr(m, '__version__', '')}")
    except ImportError:
        print(f"[NO] {mod}")

import re
import requests

COOKIES = [
    ("__ddg1_", "qAaf8GmCD2qiNP9TibTZ", ".1c.ru"),
    ("__ddg10_", "1793185193", ".1c.ru"),
    ("__ddg8_", "gbusuDNdjRBPyyFq", ".1c.ru"),
    ("__ddg9_", "213.59.153.39", ".1c.ru"),
    ("_ym_d", "1788866799", ".1c.ru"),
    ("_ym_isad", "2", ".1c.ru"),
    ("_ym_uid", "1788866799233033365", ".1c.ru"),
    ("BITRIX_SM_LOGIN", "08576-80", ".its.1c.ru"),
    ("BUS_REFERER", "https%3A%2F%2Fits.1c.ru%2Fdb%2Fintgr83%2Fcontent%2F47%2Fhdoc", ".its.1c.ru"),
]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.8078.48 Safari/537.36")

s = requests.Session()
for name, value, domain in COOKIES:
    s.cookies.set(name, value, domain=domain, path="/")
s.headers.update({"User-Agent": UA, "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"})

r = s.get("https://its.1c.ru/db/intgr83/content/47/hdoc", timeout=30)
print(f"\ncontent/47: HTTP {r.status_code} len={len(r.text)}")
out = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_sample_47.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(r.text)
print(f"[OK] сохранено: {out}")

# Кандидаты на контейнер контента
for pat in [r'<article[^>]*>', r'<div[^>]*class="[^"]*(?:content|article|text|doc|body)[^"]*"[^>]*>',
            r'<h1[^>]*>.*?</h1>']:
    ms = re.findall(pat, r.text, re.S | re.I)
    print(f"pattern {pat[:50]!r}: {len(ms)} совпадений")
    for m in ms[:5]:
        print("   ", m[:150].replace("\n", " "))
