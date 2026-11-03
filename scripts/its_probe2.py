# -*- coding: utf-8 -*-
"""Извлекаем srcdoc из iframe и смотрим структуру статьи."""
from bs4 import BeautifulSoup

html = open(r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_sample_47.html", encoding="utf-8").read()
soup = BeautifulSoup(html, "lxml")

iframe = soup.find("iframe", id="w_metadata_doc_frame")
print("iframe найден:", iframe is not None)
if iframe:
    print("src:", iframe.get("src"))
    srcdoc = iframe.get("srcdoc")
    print("srcdoc длина:", len(srcdoc) if srcdoc else None)
    # Сохраняем декодированный srcdoc
    out = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_article_47.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(srcdoc)
    print("[OK] сохранено:", out)

    # Структура статьи
    art = BeautifulSoup(srcdoc, "lxml")
    print("\n--- Тег <body> ---")
    body = art.find("body")
    print("body есть:", body is not None)
    if body:
        # Прямые дети body
        kids = [c.name for c in body.children if getattr(c, "name", None)]
        print("прямые дети body:", kids[:30])
    # Заголовки
    for tag in ["h1", "h2", "h3", "h4"]:
        ms = art.find_all(tag)
        print(f"<{tag}>: {len(ms)}", [m.get_text(strip=True)[:40] for m in ms[:3]])
    # Таблицы, pre, code
    print("tables:", len(art.find_all("table")))
    print("pre:", len(art.find_all("pre")))
    print("code:", len(art.find_all("code")))
    print("img:", len(art.find_all("img")))
    # Первый кусок текста
    txt = art.get_text(" ", strip=True)
    print("\n--- Текст (первые 600 символов) ---")
    print(txt[:600])
