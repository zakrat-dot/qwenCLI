# -*- coding: utf-8 -*-
"""Контраст: доступная (pid=8) vs ограниченная (pid=93) страница.
Проверяем реальный контент через src-URL и srcdoc."""
import json
import sys
sys.path.insert(0, r"C:\AI_PROJECTS\QWEN_LOC\scripts")
import requests
from bs4 import BeautifulSoup

with open(r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages\_session_cookies.json", encoding="utf-8") as f:
    cookies = json.load(f)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.8078.48 Safari/537.36")
s = requests.Session()
for c in cookies:
    s.cookies.set(c["name"], c["value"], domain=c["domain"], path=c["path"])
s.headers.update({
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
})
HOME = "https://its.1c.ru/db/intgr83"

def probe(pid):
    url = f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc"
    r = s.get(url, timeout=30, headers={"Referer": HOME})
    soup = BeautifulSoup(r.text, "lxml")
    iframe = soup.find("iframe", id="w_metadata_doc_frame")
    if not iframe:
        return f"pid={pid}: iframe НЕТ (HTTP {r.status_code})"
    if iframe.get("srcdoc"):
        sd = iframe["srcdoc"]
        t = BeautifulSoup(sd, "lxml").get_text(" ", strip=True)
        return f"pid={pid}: ДОСТУПНО srcdoc len={len(sd)} text={len(t)} | {t[:120]}"
    src = iframe.get("src")
    # пробуем src
    rs = s.get("https://its.1c.ru" + src, timeout=30, headers={"Referer": HOME})
    ts = BeautifulSoup(rs.text, "lxml").get_text(" ", strip=True)
    return f"pid={pid}: ОГРАНИЧЕНО src={src} (HTTP {rs.status_code}) | {ts[:120]}"

for pid in [8, 12, 28, 93, 33, 5]:
    print(probe(pid))
    print()
