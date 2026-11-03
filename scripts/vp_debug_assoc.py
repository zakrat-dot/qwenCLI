# -*- coding: utf-8 -*-
"""Дебаг: почему parse_endpoints не находит концы ассоциаций"""
import sqlite3, re

VPP = r"C:\Users\MZ3\Documents\VPProjects\elkomp28-07-25.vpp"
con = sqlite3.connect(VPP)
cur = con.cursor()

rows = cur.execute(
    "SELECT ID, NAME, DEFINITION FROM MODEL_ELEMENT WHERE MODEL_TYPE='Association' LIMIT 5"
).fetchall()

for eid, name, defn in rows:
    d = defn.decode("utf-8", errors="replace") if defn else ""
    print("=" * 60)
    print("ID:", eid, "NAME:", name, "LEN:", len(d))
    print("has 'to={':", "to={" in d, " has 'from={':", "from={" in d)
    print("EndModelElement count:", len(re.findall(r'EndModelElement=<([^>]+)>', d)))
    print("type=<...> count:", len(re.findall(r'type=<([^>]+)>', d)))
    # показать фрагменты вокруг to= и from=
    i = d.find("to=")
    if i >= 0:
        print("  ...to= фрагмент:", repr(d[i:i+200]))
    j = d.find("from=")
    if j >= 0:
        print("  ...from= фрагмент:", repr(d[j:j+200]))
