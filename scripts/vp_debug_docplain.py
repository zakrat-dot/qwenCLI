# -*- coding: utf-8 -*-
"""Дебаг 5: documentation_plain у UseCase и NOTE — статистика"""
import sqlite3, re

VPP = r"C:\Users\MZ3\Documents\VPProjects\elkomp28-07-25.vpp"
con = sqlite3.connect(VPP)
cur = con.cursor()

for mtype in ("UseCase", "NOTE"):
    total = 0
    has_plain = 0
    plain_nonempty = 0
    samples = []
    for eid, name, defn in cur.execute(
        "SELECT ID, NAME, DEFINITION FROM MODEL_ELEMENT WHERE MODEL_TYPE=?", (mtype,)
    ):
        d = defn.decode("utf-8", errors="replace") if defn else ""
        total += 1
        m = re.search(r'documentation_plain="((?:[^"\\]|\\.)*)"', d, re.DOTALL)
        if m:
            has_plain += 1
            v = m.group(1).strip()
            if v:
                plain_nonempty += 1
                if len(samples) < 3:
                    samples.append((name, v[:120]))
    print(f"{mtype}: всего={total} с documentation_plain={has_plain} непустых={plain_nonempty}")
    for s in samples:
        print("   ", s)
    print()
