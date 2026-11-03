# -*- coding: utf-8 -*-
"""Сканируем ВСЕ страницы книги: какие доступны (srcdoc), какие ограничены (src->401).
Сохраняем доступный контент в scripts/its_pages/page_<id>.html. Резюмируем в JSON."""
import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup

HOME = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_intgr83_home.html"
OUTDIR = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages"
os.makedirs(OUTDIR, exist_ok=True)

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

# Список страниц из оглавления
html = open(HOME, encoding="utf-8").read()
ids = sorted(set(int(m) for m in re.findall(r"/db/intgr83/content/(\d+)/hdoc", html)))
ids = [i for i in ids if i != 999999]
print(f"Всего страниц в оглавлении: {len(ids)} (min={ids[0]}, max={ids[-1]})")

s = requests.Session()
for name, value, domain in COOKIES:
    s.cookies.set(name, value, domain=domain, path="/")
s.headers.update({"User-Agent": UA, "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"})

accessible = []
restricted = []
errors = []

for n, pid in enumerate(ids, 1):
    out = os.path.join(OUTDIR, f"page_{pid}.html")
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        accessible.append(pid)
        continue
    try:
        r = s.get(f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc", timeout=30)
        soup = BeautifulSoup(r.text, "lxml")
        iframe = soup.find("iframe", id="w_metadata_doc_frame")
        srcdoc = iframe.get("srcdoc") if iframe else None
        if srcdoc:
            with open(out, "w", encoding="utf-8") as f:
                f.write(srcdoc)
            accessible.append(pid)
        else:
            restricted.append(pid)
    except Exception as e:
        errors.append((pid, str(e)))
    if n % 25 == 0:
        print(f"  ...{n}/{len(ids)} (доступно={len(accessible)}, ограничено={len(restricted)}, ошибок={len(errors)})")
    time.sleep(0.12)

print("\n===== ИТОГ =====")
print(f"Всего: {len(ids)}")
print(f"Доступно (srcdoc): {len(accessible)}")
print(f"Ограничено (src->401): {len(restricted)}")
print(f"Ошибки: {len(errors)}")
print("\nДоступные id:", accessible)
print("\nОграниченные id (первые 40):", restricted[:40])
if errors:
    print("\nОшибки:", errors[:10])

summary = {
    "total": len(ids),
    "accessible": accessible,
    "restricted": restricted,
    "errors": errors,
}
with open(os.path.join(OUTDIR, "_scan_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"\n[OK] резюме: {os.path.join(OUTDIR, '_scan_summary.json')}")
