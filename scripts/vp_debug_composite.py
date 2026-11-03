# -*- coding: utf-8 -*-
"""Дебаг 3: составные ссылки <контейнер>:<элемент> — проверка разрешения"""
import sys
sys.path.insert(0, r"C:\AI_PROJECTS\QWEN_LOC\scripts")
from vp_to_rag import load, parse_endpoints

VPP = r"C:\Users\MZ3\Documents\VPProjects\elkomp28-07-25.vpp"
elems, diagrams, elem_diagrams = load(VPP)
ids = set(elems.keys())

def resolve(x):
    """Составная ссылка <контейнер>:<элемент> -> берём часть после последнего ':'."""
    if x and ":" in x:
        return x.split(":")[-1]
    return x

ok = bad = 0
bad_samples = []
for e in elems.values():
    if e["type"] != "Association":
        continue
    to_id, from_id = parse_endpoints(e["defn"])
    for x in (to_id, from_id):
        if not x:
            continue
        if resolve(x) in ids:
            ok += 1
        else:
            bad += 1
            if len(bad_samples) < 8:
                bad_samples.append(x)

print("Концов ассоциаций, разрешённых в elems:", ok)
print("Не разрешилось:", bad)
print("Примеры не разрешившихся:", bad_samples)

# Проверим: часть ПЕРЕД двоеточием — всегда контейнер (Subsystem/Package/UseCase)?
from collections import Counter
before_types = Counter()
after_types = Counter()
for e in elems.values():
    if e["type"] != "Association":
        continue
    to_id, from_id = parse_endpoints(e["defn"])
    for x in (to_id, from_id):
        if x and ":" in x:
            b, a = x.split(":", 1)
            if b in ids:
                before_types[elems[b]["type"]] += 1
            if a in ids:
                after_types[elems[a]["type"]] += 1
print()
print("Типы части ПЕРЕД ':' (контейнер):", dict(before_types))
print("Типы части ПОСЛЕ ':' (элемент):", dict(after_types))
