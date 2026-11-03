# -*- coding: utf-8 -*-
"""Дебаг: найти строки NAME, которые не декодируются как UTF-8 (через CAST AS BLOB)"""
import sqlite3

VPP = r"C:\Users\MZ3\AppData\Roaming\VisualParadigm\dashbord\teamwork_client\projects\Дашборд и AI\Дашборд и AI.vpp"
con = sqlite3.connect(VPP)
cur = con.cursor()

bad = []
total = 0
for row in cur.execute("SELECT ID, CAST(NAME AS BLOB) FROM MODEL_ELEMENT"):
    eid, raw = row
    total += 1
    if raw is None:
        continue
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as e:
        bad.append((eid, raw, str(e)))

print("Всего строк:", total)
print("Проблемных:", len(bad))
for eid, raw, err in bad[:10]:
    print("=" * 50)
    print("ID:", eid)
    print("hex:", raw.hex())
    print("err:", err)
    for enc in ("cp1251", "latin-1", "utf-16-le", "cp866"):
        try:
            s = raw.decode(enc)
            print("  ", enc, "->", repr(s[:80]))
        except Exception as e:
            print("  ", enc, "ERR", e)
