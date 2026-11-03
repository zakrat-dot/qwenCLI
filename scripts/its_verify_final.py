# -*- coding: utf-8 -*-
"""Финальная проверка целостности книги в Obsidian."""
import os

obs = r"C:\Voult\Volt\1c\Книги1сИтс\Технологии интеграции"
img = os.path.join(obs, "images")

# Проверка сигнатур картинок
png = jpg = gif = other = 0
for f in os.listdir(img):
    p = os.path.join(img, f)
    with open(p, "rb") as fh:
        sig = fh.read(8)
    if sig[:8] == b"\x89PNG\r\n\x1a\n":
        png += 1
    elif sig[:3] == b"\xff\xd8\xff":
        jpg += 1
    elif sig[:6] in (b"GIF87a", b"GIF89a"):
        gif += 1
    else:
        other += 1
print(f"Картинки: PNG={png} JPG={jpg} GIF={gif} другие={other}")

# Итог по MD
mds = [f for f in os.listdir(obs) if f.endswith(".md")]
pages = [f for f in mds if f != "TOC.md"]
empty = [f for f in pages if os.path.getsize(os.path.join(obs, f)) < 500]
print(f"Всего MD: {len(mds)} (страниц: {len(pages)}, TOC: {'да' if 'TOC.md' in mds else 'НЕТ'})")
print(f"Пустых страниц (<500 байт): {len(empty)}")
if empty:
    print("  Пустые:", empty[:10])

# Размер папки картинок
total_bytes = sum(os.path.getsize(os.path.join(img, f)) for f in os.listdir(img))
print(f"Общий размер картинок: {total_bytes/1024/1024:.1f} МБ")
