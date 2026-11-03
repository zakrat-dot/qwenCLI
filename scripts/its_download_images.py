# -*- coding: utf-8 -*-
"""Скачивает ВСЕ картинки из raw HTML (правильный паттерн /db/content/intgr83/src/)
и обновляет MD-ссылки в Obsidian на локальные файлы."""
import json
import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup

BASE = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages"
RAW = os.path.join(BASE, "raw")
OBSIDIAN = r"C:\Voult\Volt\1c\Книги1сИтс\Технологии интеграции"
IMAGES_DIR = os.path.join(OBSIDIAN, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

COOKIES = os.path.join(BASE, "_session_cookies.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.8078.48 Safari/537.36")
IMG_BASE = "https://its.1c.ru/db/content/intgr83/src/"

def load_session():
    with open(COOKIES, encoding="utf-8") as f:
        cookies = json.load(f)
    s = requests.Session()
    for c in cookies:
        s.cookies.set(c["name"], c["value"], domain=c["domain"], path=c["path"])
    s.headers.update({
        "User-Agent": UA,
        "Accept": "image/png,image/jpeg,image/gif,image/webp,*/*;q=0.8",
        "Referer": "https://its.1c.ru/db/intgr83",
    })
    return s

def main():
    s = load_session()
    print("Прогрев...")
    r0 = s.get("https://its.1c.ru/db/intgr83", timeout=40)
    print(f"  HOME HTTP {r0.status_code}")
    time.sleep(1.0)

    # Собираем все ОТСОСИТЕЛЬНЫЕ картинки из raw HTML (имя + токен)
    images = {}  # file_name -> token (или None)
    for fname in sorted(os.listdir(RAW)):
        if not fname.endswith(".html"):
            continue
        html = open(os.path.join(RAW, fname), encoding="utf-8").read()
        soup = BeautifulSoup(html, "lxml")
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            # Пропускаем абсолютные URL (трекинг и т.п.)
            if src.startswith("http://") or src.startswith("https://") or src.startswith("//"):
                continue
            # Разделяем имя и токен
            if "?" in src:
                file_name, query = src.split("?", 1)
                m = re.search(r"_=([^&]+)", query)
                token = m.group(1) if m else None
            else:
                file_name, token = src, None
            file_name = file_name.strip()
            if not file_name:
                continue
            if file_name not in images:
                images[file_name] = token

    print(f"Найдено уникальных картинок: {len(images)}")

    # Скачиваем
    downloaded = {}
    failed = []
    for i, (file_name, token) in enumerate(images.items(), 1):
        local_path = os.path.join(IMAGES_DIR, file_name)
        if os.path.exists(local_path) and os.path.getsize(local_path) > 100:
            downloaded[file_name] = local_path
            continue

        url = IMG_BASE + file_name
        if token:
            url += "?_=" + token

        ok = False
        for attempt in range(3):
            try:
                r = s.get(url, timeout=40)
                if r.status_code == 200 and len(r.content) > 100:
                    with open(local_path, "wb") as f:
                        f.write(r.content)
                    downloaded[file_name] = local_path
                    ok = True
                    break
                else:
                    # Попробуем без токена
                    if token:
                        url = IMG_BASE + file_name
                    else:
                        break
            except Exception as e:
                if attempt == 2:
                    failed.append({"file": file_name, "url": url, "error": str(e)})
        if not ok:
            if not any(f["file"] == file_name for f in failed):
                failed.append({"file": file_name, "url": url})

        if i % 20 == 0 or i == len(images):
            print(f"  [{i}/{len(images)}] скачано={len(downloaded)} ошибок={len(failed)}")
        time.sleep(random.uniform(0.2, 0.5))

    print(f"\nСкачано: {len(downloaded)}, Ошибок: {len(failed)}")
    if failed:
        print("Не скачались:")
        for f in failed[:20]:
            print(f"  {f['file']}  {f.get('url','')}")

    # Обновляем MD файлы — заменяем ссылки на картинки
    print("\nОбновляем MD файлы...")
    updated = 0
    for fname in os.listdir(OBSIDIAN):
        if not fname.endswith(".md") or fname == "TOC.md":
            continue
        fpath = os.path.join(OBSIDIAN, fname)
        content = open(fpath, encoding="utf-8").read()
        new_content = content
        for file_name in images:
            # ![image](01_02.png?_=0000153266FEEB6F-v2) -> ![image](images/01_02.png)
            pattern = re.compile(r'!\[[^\]]*\]\(' + re.escape(file_name) + r'(?:\?[^)]*)?\)')
            if pattern.search(new_content):
                new_content = pattern.sub(f'![image](images/{file_name})', new_content)
        if new_content != content:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            updated += 1

    print(f"Обновлено MD файлов: {updated}")

    # Сохраняем сводку
    summary = {
        "total": len(images),
        "downloaded": len(downloaded),
        "failed": len(failed),
        "failed_list": failed,
        "image_base": IMG_BASE,
    }
    with open(os.path.join(BASE, "_images_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\nГотово.")

if __name__ == "__main__":
    main()
