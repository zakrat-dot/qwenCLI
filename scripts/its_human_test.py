# -*- coding: utf-8 -*-
"""Тест гипотезы «защита от быстрых запросов»: имитация человека.
Прогрев главной страницы -> случайные задержки 2-4с -> Referer=главная.
Смотрим, откроются ли ранее заблокированные 93/33/5."""
import random
import time
import requests
from bs4 import BeautifulSoup

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
HOME = "https://its.1c.ru/db/intgr83"

s = requests.Session()
for name, value, domain in COOKIES:
    s.cookies.set(name, value, domain=domain, path="/")
s.headers.update({
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
})

def human_pause():
    d = random.uniform(2.0, 4.0)
    print(f"  ... пауза {d:.1f}с")
    time.sleep(d)

def classify(r):
    soup = BeautifulSoup(r.text, "lxml")
    iframe = soup.find("iframe", id="w_metadata_doc_frame")
    if not iframe:
        return f"iframe НЕТ (HTTP {r.status_code})"
    if iframe.get("srcdoc"):
        return f"ДОСТУПНО (srcdoc len={len(iframe['srcdoc'])})"
    src = iframe.get("src")
    if src:
        return f"ОГРАНИЧЕНО (src={src})"
    return "ни srcdoc, ни src"

print("=== 1) Прогрев: главная страница книги ===")
r0 = s.get(HOME, timeout=30)
print(f"  HOME HTTP {r0.status_code} len={len(r0.text)}")
sc = r0.headers.get("Set-Cookie")
print("  Set-Cookie:", sc if sc else "(нет)")
print("  Куки сессии после главной:")
for c in s.cookies:
    if "1c.ru" in (c.domain or ""):
        print(f"    {c.name} = {c.value[:35]}  (domain={c.domain})")

human_pause()

print("\n=== 2) Запрос к ранее заблокированным страницам (как человек) ===")
for pid in [93, 33, 5, 47]:
    url = f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc"
    r = s.get(url, timeout=30, headers={"Referer": HOME})
    print(f"  pid={pid}: {classify(r)}")
    human_pause()
