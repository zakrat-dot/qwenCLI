# -*- coding: utf-8 -*-
"""Разведка 2: иерархия, USER_ID, пакеты, как найти реальную модель"""
import sqlite3

VPP = r"C:\Users\MZ3\Documents\VPProjects\elkomp28-07-25.vpp"
con = sqlite3.connect(VPP)
cur = con.cursor()

# Загрузим все элементы в словарь для обхода дерева
elems = {}
for r in cur.execute("SELECT ID, USER_ID, MODEL_TYPE, PARENT_ID, NAME FROM MODEL_ELEMENT"):
    elems[r[0]] = {"user_id": r[1], "type": r[2], "parent": r[3], "name": r[4]}

def chain(eid, depth=0):
    out = []
    cur_id = eid
    while cur_id and cur_id in elems and depth < 15:
        e = elems[cur_id]
        out.append("  " * depth + f"[{e['type']}] {e['name']!r}  (ID={cur_id}, USER_ID={e['user_id']})")
        cur_id = e["parent"]
        depth += 1
    return out

print("=== Цепочка родителей для нескольких UseCase ===")
ucs = [eid for eid, e in elems.items() if e["type"] == "UseCase" and e["name"]][:5]
for u in ucs:
    print("---")
    for line in chain(u):
        print(line)

print()
print("=== Все Package (и их родитель) ===")
for eid, e in elems.items():
    if e["type"] == "Package":
        p = elems.get(e["parent"], {})
        print(f"PKG {e['name']!r} ID={eid} USER_ID={e['user_id']}  <- parent [{p.get('type')}] {p.get('name')!r}")

print()
print("=== USER_ID: сколько заполнено по типам ===")
for r in cur.execute(
    "SELECT MODEL_TYPE, COUNT(*), SUM(CASE WHEN USER_ID IS NOT NULL THEN 1 ELSE 0 END) "
    "FROM MODEL_ELEMENT GROUP BY MODEL_TYPE ORDER BY 2 DESC LIMIT 15"
):
    print(r)

print()
print("=== Элементы с USER_ID (образцы) ===")
for r in cur.execute(
    "SELECT MODEL_TYPE, USER_ID, NAME FROM MODEL_ELEMENT WHERE USER_ID IS NOT NULL LIMIT 15"
):
    print(r)
