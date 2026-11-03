# -*- coding: utf-8 -*-
"""Скачивает ВСЕ 257 страниц книги intgr83 с its.1c.ru.
- Использует куки сессии из _session_cookies.json
- Прогрев главной страницы перед стартом
- Пейсинг 0.8-1.6с между запросами (защита от rate-limit)
- Ретраи (3 попытки) при 401/ошибке
- Resume: пропускает уже скачанные страницы
- Сохраняет raw HTML в raw/NNN.html + сводку _download_summary.json
- Лог в _download.log
"""
import json
import os
import random
import sys
import time
import requests
from bs4 import BeautifulSoup

BASE = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages"
RAW = os.path.join(BASE, "raw")
os.makedirs(RAW, exist_ok=True)
LOG = os.path.join(BASE, "_download.log")
SUMMARY = os.path.join(BASE, "_download_summary.json")
COOKIES = os.path.join(BASE, "_session_cookies.json")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.8078.48 Safari/537.36")
HOME = "https://its.1c.ru/db/intgr83"
TOTAL = 257

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_session():
    with open(COOKIES, encoding="utf-8") as f:
        cookies = json.load(f)
    s = requests.Session()
    for c in cookies:
        s.cookies.set(c["name"], c["value"], domain=c["domain"], path=c["path"])
    s.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Referer": HOME,
    })
    return s

def extract_content(s, pid):
    """Возвращает (html, status). status: ok|restricted|error"""
    url = f"https://its.1c.ru/db/intgr83/content/{pid}/hdoc"
    r = s.get(url, timeout=40)
    if r.status_code == 401:
        return None, "restricted"
    soup = BeautifulSoup(r.text, "lxml")
    iframe = soup.find("iframe", id="w_metadata_doc_frame")
    if not iframe:
        return None, "error"
    if iframe.get("srcdoc"):
        return iframe["srcdoc"], "ok"
    src = iframe.get("src")
    if src:
        rs = s.get("https://its.1c.ru" + src, timeout=40)
        if rs.status_code == 401:
            return None, "restricted"
        return rs.text, "ok"
    return None, "error"

def main():
    # Загружаем существующую сводку (resume)
    summary = {}
    if os.path.exists(SUMMARY):
        with open(SUMMARY, encoding="utf-8") as f:
            summary = json.load(f)

    s = load_session()

    # Прогрев
    log("Прогрев главной страницы...")
    try:
        r0 = s.get(HOME, timeout=40)
        log(f"  HOME HTTP {r0.status_code} len={len(r0.text)}")
    except Exception as e:
        log(f"  HOME error: {e}")
    time.sleep(random.uniform(1.0, 2.0))

    ok = restricted = error = skipped = 0
    for pid in range(1, TOTAL + 1):
        fname = os.path.join(RAW, f"{pid:03d}.html")
        # Resume
        if os.path.exists(fname) and os.path.getsize(fname) > 500:
            skipped += 1
            continue

        html = None
        status = "error"
        for attempt in range(1, 4):
            try:
                html, status = extract_content(s, pid)
            except Exception as e:
                status = "error"
                html = None
                log(f"  pid={pid} attempt {attempt} exception: {e}")
            if status == "ok":
                break
            # restricted или error — пауза и ретрай
            time.sleep(random.uniform(2.0, 4.0) * attempt)

        if status == "ok" and html:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(html)
            summary[str(pid)] = {"status": "ok", "len": len(html)}
            ok += 1
            log(f"pid={pid:3d} OK len={len(html)}")
        else:
            summary[str(pid)] = {"status": status}
            if status == "restricted":
                restricted += 1
                log(f"pid={pid:3d} RESTRICTED")
            else:
                error += 1
                log(f"pid={pid:3d} ERROR")

        # Пейсинг
        time.sleep(random.uniform(0.8, 1.6))

    # Сохраняем сводку
    with open(SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    log("=" * 50)
    log(f"ИТОГО: ok={ok} restricted={restricted} error={error} skipped={skipped} (всего {TOTAL})")
    log("Готово.")

if __name__ == "__main__":
    main()
