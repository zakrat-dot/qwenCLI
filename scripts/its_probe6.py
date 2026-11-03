# -*- coding: utf-8 -*-
"""Проверяем: ставит ли hdoc-ответ Set-Cookie, которого не хватает для src."""
import requests
from bs4 import BeautifulSoup

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

pid = 33
r = s.get(f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc", timeout=30)
print("=== hdoc response headers (Set-Cookie) ===")
sc = r.headers.get("Set-Cookie")
print("Set-Cookie:", sc if sc else "(нет)")
print("\n=== Все куки в сессии после hdoc ===")
for c in s.cookies:
    print(f"  {c.name} = {c.value[:40]}  (domain={c.domain}, path={c.path})")

# src URL
soup = BeautifulSoup(r.text, "lxml")
iframe = soup.find("iframe", id="w_metadata_doc_frame")
src = iframe.get("src")
print(f"\n=== src = {src} ===")

# Попробуем src с разными заголовками
for label, extra in [
    ("без доп.", {}),
    ("Referer", {"Referer": f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc"}),
    ("Referer+XFW", {"Referer": f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc",
                     "X-Requested-With": "XMLHttpRequest"}),
    ("Origin", {"Origin": "https://its.1c.ru",
                "Referer": f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc"}),
]:
    r2 = s.get("https://its.1c.ru" + src, timeout=30, headers=extra)
    ok = "OK" if r2.status_code == 200 and len(r2.text) > 5000 else "401/limited"
    print(f"  [{label}] HTTP {r2.status_code} len={len(r2.text)} -> {ok}")
