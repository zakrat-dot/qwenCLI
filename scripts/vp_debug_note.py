# -*- coding: utf-8 -*-
"""Дебаг 4: где в NOTE хранится читаемый текст"""
import sqlite3, re

VPP = r"C:\Users\MZ3\Documents\VPProjects\elkomp28-07-25.vpp"
con = sqlite3.connect(VPP)
cur = con.cursor()

# Возьмём NOTE с непустым NAME и NOTE с пустым
print("=== NOTE с NAME (первые 3) ===")
for eid, name, defn in cur.execute(
    "SELECT ID, NAME, DEFINITION FROM MODEL_ELEMENT WHERE MODEL_TYPE='NOTE' AND NAME IS NOT NULL AND NAME != '' LIMIT 3"
):
    d = defn.decode("utf-8", errors="replace") if defn else ""
    print("=" * 60)
    print("ID:", eid, "NAME:", repr(name), "LEN:", len(d))
    print(repr(d[:1200]))

print()
print("=== NOTE с пустым NAME (первые 2) ===")
for eid, name, defn in cur.execute(
    "SELECT ID, NAME, DEFINITION FROM MODEL_ELEMENT WHERE MODEL_TYPE='NOTE' AND (NAME IS NULL OR NAME='') LIMIT 2"
):
    d = defn.decode("utf-8", errors="replace") if defn else ""
    print("=" * 60)
    print("ID:", eid, "NAME:", repr(name), "LEN:", len(d))
    print(repr(d[:1200]))
