# -*- coding: utf-8 -*-
"""Тест: вытащить куки its.1c.ru из Chrome и открыть страницу книги intgr83."""
import sys
import traceback

DOMAIN = "its.1c.ru"
URL = "https://its.1c.ru/db/intgr83"

def main():
    import browser_cookie3
    import requests

    print("== 1. Извлекаю куки из Chrome ==")
    try:
        cj = browser_cookie3.chrome(domain_name=DOMAIN)
    except Exception as e:
        print(f"[FAIL] browser_cookie3.chrome(): {type(e).__name__}: {e}")
        traceback.print_exc()
        # Пробуем без фильтра домена
        try:
            print("== Повтор без domain_name ==")
            cj = browser_cookie3.chrome()
        except Exception as e2:
            print(f"[FAIL] browser_cookie3.chrome() (без домена): {type(e2).__name__}: {e2}")
            return 1

    cookies = list(cj)
    print(f"Куки всего: {len(cookies)}")
    for c in cookies[:40]:
        print(f"  - {c.name} = {c.value[:40]}{'...' if len(c.value) > 40 else ''}  (domain={c.domain}, path={c.path})")

    if not cookies:
        print("[WARN] Куки для its.1c.ru не найдены. Возможно, ты не залогинен в Chrome,")
        print("       или используешь другой профиль/браузер.")
        return 2

    print("\n== 2. Открываю страницу книги ==")
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Referer": "https://its.1c.ru/",
    }
    try:
        r = requests.get(URL, cookies=cj, headers=headers, timeout=30, allow_redirects=True)
    except Exception as e:
        print(f"[FAIL] requests.get: {type(e).__name__}: {e}")
        return 3

    print(f"HTTP {r.status_code}  final_url={r.url}  len={len(r.text)}")
    ct = r.headers.get("Content-Type", "")
    print(f"Content-Type: {ct}")

    # Ищем заголовок и признаки авторизации
    import re
    low = r.text
    m = re.search(r"<title[^>]*>(.*?)</title>", low, re.S | re.I)
    if m:
        print(f"<title>: {m.group(1).strip()[:200]}")

    for marker in ["авториз", "вход", "login", "Авторизуйтесь", "не авторизован", "oauth", "passport"]:
        if marker.lower() in low.lower():
            idx = low.lower().find(marker.lower())
            snippet = low[max(0, idx - 60): idx + 80].replace("\n", " ")
            print(f"[marker] '{marker}': ...{snippet}...")

    # Сохраним HTML для анализа
    out = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_intgr83_home.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(r.text)
    print(f"\n[OK] HTML сохранён: {out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
