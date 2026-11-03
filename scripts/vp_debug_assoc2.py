# -*- coding: utf-8 -*-
"""Дебаг 2: прогон parse_endpoints по ВСЕМ ассоциациям"""
import sqlite3, re, sys
sys.path.insert(0, r"C:\AI_PROJECTS\QWEN_LOC\scripts")
from vp_to_rag import parse_endpoints, load

VPP = r"C:\Users\MZ3\Documents\VPProjects\elkomp28-07-25.vpp"
elems, diagrams, elem_diagrams = load(VPP)

assoc = [e for e in elems.values() if e["type"] == "Association"]
print("Всего Association:", len(assoc))

ok_both = ok_to = ok_from = 0
to_in = from_in = 0
samples_fail = []
for e in assoc:
    to_id, from_id = parse_endpoints(e["defn"])
    if to_id:
        ok_to += 1
        if to_id in elems:
            to_in += 1
    if from_id:
        ok_from += 1
        if from_id in elems:
            from_in += 1
    if to_id and from_id and to_id in elems and from_id in elems:
        ok_both += 1
    elif len(samples_fail) < 5:
        samples_fail.append((e["id"], to_id, from_id,
                             to_id in elems if to_id else None,
                             from_id in elems if from_id else None))

print("to_id распарсено:", ok_to, " из них в elems:", to_in)
print("from_id распарсено:", ok_from, " из них в elems:", from_in)
print("оба валидны и в elems:", ok_both)
print()
print("Примеры 'провалов':")
for s in samples_fail:
    print("  ", s)

# Проверим: на что указывают концы — какие типы элементов
from collections import Counter
types = Counter()
for e in assoc:
    to_id, from_id = parse_endpoints(e["defn"])
    for x in (to_id, from_id):
        if x in elems:
            types[elems[x]["type"]] += 1
print()
print("Типы элементов-концов:", dict(types))
