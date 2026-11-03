# -*- coding: utf-8 -*-
"""Дебаг: какая кодировка в колонке NAME у проекта «Дашборд и AI»"""
import sqlite3

VPP = r"C:\Users\MZ3\AppData\Roaming\VisualParadigm\dashbord\teamwork_client\projects\Дашборд и AI\Дашборд и AI.vpp"
con = sqlite3.connect(VPP)
cur = con.cursor()

# Берём сырые байты NAME (TEXT может быть в cp1251/latin1)
print("=== Первые 10 NAME (сырые байты) ===")
for eid, name in cur.execute("SELECT ID, NAME FROM MODEL_ELEMENT LIMIT 10"):
    if name is None:
        print(eid, "NULL")
        continue
    # sqlite3 вернул str (уже декодировал) или bytes?
    if isinstance(name, bytes):
        raw = name
    else:
        raw = name.encode("utf-8", errors="replace")
    print(eid, "len=", len(raw), "hex=", raw[:40].hex())
    for enc in ("utf-8", "cp1251", "latin-1", "utf-16-le"):
        try:
            s = raw.decode(enc)
            print("   ", enc, "->", repr(s[:60]))
        except Exception as e:
            print("   ", enc, "ERR", e)
    print()
