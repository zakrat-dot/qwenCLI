# -*- coding: utf-8 -*-
"""Проверка доступа к its.1c.ru/db/intgr83 с куками, скопированными из DevTools."""
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

def main():
    s = requests.Session()
    for name, value, domain in COOKIES:
        s.cookies.set(name, value, domain=domain, path="/")
    s.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    })
    url = "https://its.1c.ru/db/intgr83"
    r = s.get(url, timeout=30, allow_redirects=True)
    print(f"HTTP {r.status_code}  final_url={r.url}  len={len(r.text)}")
    m = re.search(r"<title[^>]*>(.*?)</title>", r.text, re.S | re.I)
    if m:
        print(f"<title>: {m.group(1).strip()[:200]}")
    low = r.text.lower()
    for marker in ["авториз", "войти", "login", "oauth", "passport", "не авторизован", "интеграция"]:
        idx = low.find(marker)
        if idx >= 0:
            snippet = r.text[max(0, idx - 60): idx + 80].replace("\n", " ")
            print(f"[marker] '{marker}': ...{snippet}...")
    out = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_intgr83_home.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(r.text)
    print(f"[OK] HTML сохранён: {out}")

if __name__ == "__main__":
    main()
