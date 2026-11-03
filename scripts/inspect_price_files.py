# -*- coding: utf-8 -*-
"""Инспекция структуры двух прайс-файлов: листы, колонки, строки, примеры."""
import pandas as pd

FILES = {
    "NEW": r"C:\AI_PROJECTS\QWEN_LOC\Прайс_28-10-26.xlsx",
    "OLD": r"C:\AI_PROJECTS\QWEN_LOC\Прайс_002-10-26.xlsx",
}

for tag, path in FILES.items():
    print("=" * 70)
    print(f"[{tag}] {path}")
    xl = pd.ExcelFile(path)
    print("Листы:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = xl.parse(sheet, nrows=5)
        full = xl.parse(sheet, usecols=[0])
        print(f"\n--- Лист '{sheet}': ~{len(full)} строк, {len(df.columns)} колонок")
        print("Колонки:", df.columns.tolist())
        print(df.head(3).to_string(max_colwidth=40))
