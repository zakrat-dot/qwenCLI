# -*- coding: utf-8 -*-
"""Пробуем страницу с кодом: srcdoc ИЛИ src."""
import re
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

def get_article_html(pid):
    r = s.get(f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc", timeout=30)
    soup = BeautifulSoup(r.text, "lxml")
    iframe = soup.find("iframe", id="w_metadata_doc_frame")
    if not iframe:
        return None, "no-iframe", r.status_code
    srcdoc = iframe.get("srcdoc")
    if srcdoc:
        return srcdoc, "srcdoc", r.status_code
    src = iframe.get("src")
    if src:
        r2 = s.get("https://its.1c.ru" + src, timeout=30)
        return r2.text, f"src:{src}", r2.status_code
    return None, "neither", r.status_code

for pid in [33, 48]:
    html, how, status = get_article_html(pid)
    print(f"\n===== content/{pid}: via {how} (HTTP {status}) len={len(html) if html else 0} =====")
    if not html:
        continue
    art = BeautifulSoup(html, "lxml")
    print("  codebox:", len(art.find_all("div", class_="codebox")))
    print("  codeline p:", len(art.find_all("p", class_=re.compile("codeline"))))
    print("  tables:", len(art.find_all("table")))
    print("  h2:", [h.get_text(strip=True)[:40] for h in art.find_all("h2")])
    print("  h3:", [h.get_text(strip=True)[:40] for h in art.find_all("h3")])
    cb = art.find("div", class_="codebox")
    if cb:
        print("\n  --- HTML первого codebox (первые 1800 символов) ---")
        print(str(cb)[:1800])
    out = rf"C:\AI_PROJECTS\QWEN_LOC\scripts\its_article_{pid}.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [OK] сохранено: {out}")
