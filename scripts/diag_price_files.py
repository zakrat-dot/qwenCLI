# -*- coding: utf-8 -*-
"""Диагностика прайсов: групповые строки, дубликаты артикулов, разные цены внутри файла."""
import pandas as pd

FILES = [
    ("NEW", r"C:\AI_PROJECTS\QWEN_LOC\Прайс_28-10-26.xlsx"),
    ("OLD", r"C:\AI_PROJECTS\QWEN_LOC\Прайс_002-10-26.xlsx"),
]


def norm_art(x):
    if pd.isna(x):
        return ""
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x).strip()


for tag, path in FILES:
    df = pd.read_excel(path, header=3)
    df["art"] = df["Артикул"].map(norm_art)
    empty = df[df["art"] == ""]
    d = df[df["art"] != ""]
    dup_mask = d["art"].duplicated(keep=False)
    g = d.groupby("art")["Розничная цена"].nunique()
    print(f"=== {tag}: всего строк данных: {len(df)}")
    print(f"  без артикула (группы/пустые): {len(empty)}")
    if len(empty):
        print("  примеры строк без артикула:")
        print(empty[["Наименование", "НаименованиеПолное", "Розничная цена"]]
              .head(8).to_string(max_colwidth=50))
    print(f"  с артикулом: {len(d)}, уникальных: {d['art'].nunique()}")
    print(f"  строк-дубликатов артикула: {int(dup_mask.sum())} "
          f"(уникальных артикулов с дублями: {int(d[dup_mask]['art'].nunique())})")
    print(f"  артикулов с РАЗНЫМИ ценами внутри одного файла: {int((g > 1).sum())}")
    if int((g > 1).sum()):
        bad = g[g > 1].index.tolist()[:5]
        for a in bad:
            sub = d[d["art"] == a][["Наименование", "Розничная цена"]]
            print(f"    пример {a}:")
            print(sub.to_string(max_colwidth=50))
    print()
