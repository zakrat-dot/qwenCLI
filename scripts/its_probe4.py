# -*- coding: utf-8 -*-
"""Проверка: зависит ли наличие srcdoc от BUS_REFERER / запрошенной страницы."""
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
]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.8078.48 Safari/537.36")

def make_session(referer_pid):
    s = requests.Session()
    for name, value, domain in BASE_COOKIES:
        s.cookies.set(name, value, domain=domain, path="/")
    if referer_pid:
        s.cookies.set("BUS_REFERER",
                      f"https%3A%2F%2Fits.1c.ru%2Fdb%2Fintgr83%2Fcontent%2F{referer_pid}%2Fhdoc",
                      domain=".its.1c.ru", path="/")
    s.headers.update({"User-Agent": UA, "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"})
    return s

def check(pid, referer_pid, label):
    s = make_session(referer_pid)
    r = s.get(f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc", timeout=30)
    soup = BeautifulSoup(r.text, "lxml")
    iframe = soup.find("iframe", id="w_metadata_doc_frame")
    if not iframe:
        print(f"{label}: pid={pid} ref={referer_pid} -> iframe НЕТ (HTTP {r.status_code})")
        return
    srcdoc = iframe.get("srcdoc")
    src = iframe.get("src")
    print(f"{label}: pid={pid} ref={referer_pid} -> HTTP {r.status_code} "
          f"srcdoc={'ДА len='+str(len(srcdoc)) if srcdoc else 'НЕТ'} src={src}")

# 1. Текущее состояние: ref=47
check(47, 47, "A")
check(33, 47, "B")
# 2. ref=33
check(33, 33, "C")
check(47, 33, "D")
# 3. ref=None (без BUS_REFERER)
check(33, None, "E")
check(47, None, "F")
