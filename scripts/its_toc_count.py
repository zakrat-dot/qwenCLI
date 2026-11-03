# -*- coding: utf-8 -*-
"""Подсчёт страниц и глав книги intgr83 по оглавлению."""
import re

html = open(r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_intgr83_home.html", encoding="utf-8").read()
ids = sorted(set(int(m) for m in re.findall(r"/db/intgr83/content/(\d+)/hdoc", html)))
print("Всего страниц в оглавлении:", len(ids))
print("Min:", ids[0], " Max:", ids[-1])
chapters = re.findall(r'content/\d+/hdoc" target="_top">(Глава[^<]+)', html)
print("Главы:")
for c in chapters:
    print("  -", c)
