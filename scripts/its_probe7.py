# -*- coding: utf-8 -*-
"""Тест доступа с ТОЧНЫМИ куками залогиненной сессии пользователя."""
import requests
from bs4 import BeautifulSoup

# Ровно те куки, что дал пользователь (домены .1c.ru и .its.1c.ru)
COOKIES = [
    ("__ddg1_", "qAaf8GmCD2qiNP9TibTZ", ".1c.ru"),
    ("__ddg10_", "1793187534", ".1c.ru"),
    ("__ddg8_", "K2O0XAsBuc8ri4Hp", ".1c.ru"),
    ("__ddg9_", "213.59.153.39", ".1c.ru"),
    ("_ym_d", "1788866799", ".1c.ru"),
    ("_ym_isad", "2", ".1c.ru"),
    ("_ym_uid", "1788866799233033365", ".1c.ru"),
    ("client_language", "ru_RU", ".1c.ru"),
    ("BITRIX_SM_LOGIN", "08576-80", ".its.1c.ru"),
]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.8078.48 Safari/537.36")

s = requests.Session()
for name, value, domain in COOKIES:
    s.cookies.set(name, value, domain=domain, path="/")
s.headers.update({
    "User-Agent": UA,
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
})

def check(pid):
    r = s.get(f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc", timeout=30)
    soup = BeautifulSoup(r.text, "lxml")
    iframe = soup.find("iframe", id="w_metadata_doc_frame")
    if not iframe:
        print(f"pid={pid}: iframe НЕТ (HTTP {r.status_code})")
        return
    srcdoc = iframe.get("srcdoc")
    src = iframe.get("src")
    if srcdoc:
        print(f"pid={pid}: ДОСТУПНО (srcdoc len={len(srcdoc)})")
        return
    # только src -> пробуем загрузить
    if src:
        r2 = s.get("https://its.1c.ru" + src, timeout=30,
                   headers={"Referer": f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc"})
        ok = "ДОСТУПНО" if r2.status_code == 200 and len(r2.text) > 5000 else "401/ограничено"
        print(f"pid={pid}: src={src} -> HTTP {r2.status_code} len={len(r2.text)} -> {ok}")
    else:
        print(f"pid={pid}: ни srcdoc, ни src")

print("=== Проверка доступа с куками залогиненной сессии ===")
for pid in [93, 33, 47, 1, 5]:
    check(pid)

# Покажем, какие куки реально ушли в запрос
print("\n=== Куки, отправляемые для its.1c.ru ===")
for c in s.cookies:
    if "1c.ru" in (c.domain or ""):
        print(f"  {c.name} = {c.value[:30]}  (domain={c.domain})")
