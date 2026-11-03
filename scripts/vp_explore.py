# -*- coding: utf-8 -*-
"""Разведка структуры .vpp (Visual Paradigm, SQLite)"""
import sqlite3
import sys

VPP = r"C:\Users\MZ3\Documents\VPProjects\elkomp28-07-25.vpp"
con = sqlite3.connect(VPP)
cur = con.cursor()

print("=== ROOTS (PARENT_ID IS NULL) ===")
for r in cur.execute("SELECT ID, USER_ID, MODEL_TYPE, NAME FROM MODEL_ELEMENT WHERE PARENT_ID IS NULL"):
    print(r)

print()
print("=== USER_ID samples by type ===")
for r in cur.execute(
    "SELECT MODEL_TYPE, USER_ID, NAME FROM MODEL_ELEMENT "
    "WHERE USER_ID IS NOT NULL AND MODEL_TYPE IN ('UseCase','Package','Association','NOTE') LIMIT 12"
):
    print(r)

print()
print("=== UseCase DEFINITION sample (first 800 bytes) ===")
row = cur.execute(
    "SELECT NAME, DEFINITION FROM MODEL_ELEMENT WHERE MODEL_TYPE='UseCase' AND NAME IS NOT NULL LIMIT 1"
).fetchone()
print("NAME:", row[0])
print(repr(row[1][:800]))

print()
print("=== Association DEFINITION sample (first 800 bytes) ===")
row = cur.execute(
    "SELECT NAME, DEFINITION FROM MODEL_ELEMENT WHERE MODEL_TYPE='Association' LIMIT 1"
).fetchone()
print("NAME:", row[0])
print(repr(row[1][:800]))

print()
print("=== DIAGRAM_ELEMENT sample (Include shape) ===")
for r in cur.execute(
    "SELECT SHAPE_TYPE, MODEL_ELEMENT_ID, COMPOSITE_MODEL_ELEMENT_ADDRESS, REF_MODEL_ELEMENT_ADDRESS "
    "FROM DIAGRAM_ELEMENT WHERE SHAPE_TYPE LIKE '%Include%' OR SHAPE_TYPE LIKE '%Association%' LIMIT 8"
):
    print(r)

print()
print("=== SHAPE_TYPE distribution ===")
for r in cur.execute("SELECT SHAPE_TYPE, COUNT(*) FROM DIAGRAM_ELEMENT GROUP BY SHAPE_TYPE ORDER BY 2 DESC LIMIT 25"):
    print(r)
