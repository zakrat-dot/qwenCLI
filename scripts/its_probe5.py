# -*- coding: utf-8 -*-
"""Карта доступа: какие страницы имеют srcdoc, а какие только src (и статус src)."""
import requests
from bs4 import BeautifulSoup

BASE_COOKIES = [
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
for name, value, domain in BASE_COOKIES:
    s.cookies.set(name, value, domain=domain, path="/")
s.headers.update({"User-Agent": UA, "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"})

print("pid | srcdoc | src_url | src_status")
for pid in [1, 5, 6, 7, 8, 33, 47, 48, 91, 92, 117]:
    r = s.get(f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc", timeout=30)
    soup = BeautifulSoup(r.text, "lxml")
    iframe = soup.find("iframe", id="w_metadata_doc_frame")
    if not iframe:
        print(f"{pid} | iframe НЕТ (HTTP {r.status_code})")
        continue
    srcdoc = iframe.get("srcdoc")
    src = iframe.get("src")
    src_status = "-"
    if src and not srcdoc:
        r2 = s.get("https://its.1c.ru" + src, timeout=30,
                   headers={"Referer": f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc"})
        src_status = f"{r2.status_code} len={len(r2.text)}"
    print(f"{pid} | {'ДА len='+str(len(srcdoc)) if srcdoc else 'НЕТ'} | {src} | {src_status}")
