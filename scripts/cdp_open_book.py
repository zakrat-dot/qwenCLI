# -*- coding: utf-8 -*-
"""Открывает в CDP-браузере страницу книги its.1c.ru для логина."""
import sys
sys.path.insert(0, r"C:\AI_PROJECTS\QWEN_LOC\scripts")
from cdp_client import find_page_tab, CDP

tab = find_page_tab()
if not tab:
    print("Не найдена вкладка page")
    sys.exit(1)

cdp = CDP(tab)
cdp.navigate("https://its.1c.ru/db/intgr83")
print("Открыта: https://its.1c.ru/db/intgr83")
print("ВКЛАДКА:", tab["webSocketDebuggerUrl"][:60])
cdp.close()
