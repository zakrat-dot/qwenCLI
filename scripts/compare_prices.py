# -*- coding: utf-8 -*-
"""Сравнение цен по артикулу: новый прайс (28.10) vs старый прайс (02.10).

Учитывает коллизии артикулов: если один артикул в файле принадлежит
двум разным товарам — такие артикулы НЕ сравниваются по цене, а
выносятся в отдельный лист «Коллизии_артикулов» для ручной проверки.

Результат — Excel:
  - «Разница цен»      — артикулы, где цена изменилась
  - «Только в новом»   — артикулы, которых нет в старом прайсе
  - «Только в старом»  — артикулы, которых нет в новом прайсе
  - «Коллизии_артикулов» — артикулы, занятые разными товарами
"""
import pandas as pd

NEW = r"C:\AI_PROJECTS\QWEN_LOC\Прайс_28-10-26.xlsx"
OLD = r"C:\AI_PROJECTS\QWEN_LOC\Прайс_002-10-26.xlsx"
OUT = r"C:\AI_PROJECTS\QWEN_LOC\Разница_цен_28-10_vs_02-10.xlsx"
TOL = 0.001  # допуск на плавающую точку


def norm_art(x):
    """Артикул в строку: 12345.0 -> '12345', пробелы убираем."""
    if pd.isna(x):
        return ""
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x).strip()


def load(path):
    df = pd.read_excel(path, header=3)
    df["Артикул"] = df["Артикул"].map(norm_art)
    df = df[df["Артикул"] != ""]
    return df


def colliding_arts(df):
    """Артикулы, у которых в файле 2+ разных наименования (разные товары)."""
    g = df.groupby("Артикул")["Наименование"].nunique()
    return set(g[g > 1].index)


new = load(NEW)
old = load(OLD)

coll = colliding_arts(new) | colliding_arts(old)
print(f"Коллизии артикулов (разные товары под одним артикулом): {sorted(coll)}")

new_c = new[~new["Артикул"].isin(coll)].drop_duplicates(subset="Артикул", keep="first")
old_c = old[~old["Артикул"].isin(coll)].drop_duplicates(subset="Артикул", keep="first")

m = new_c[["Артикул", "Наименование", "Розничная цена"]].merge(
    old_c[["Артикул", "Розничная цена"]].rename(columns={"Розничная цена": "Цена_старая"}),
    on="Артикул",
    how="inner",
)
m = m.rename(columns={"Розничная цена": "Цена_новая"})
m["Разница"] = m["Цена_новая"] - m["Цена_старая"]

diff = m[m["Разница"].abs() > TOL].copy()
diff = diff.sort_values("Артикул")[
    ["Артикул", "Наименование", "Цена_старая", "Цена_новая", "Разница"]
]

only_new = new_c[~new_c["Артикул"].isin(old_c["Артикул"])][
    ["Артикул", "Наименование", "Розничная цена"]
].rename(columns={"Розничная цена": "Цена_новая"})
only_old = old_c[~old_c["Артикул"].isin(new_c["Артикул"])][
    ["Артикул", "Наименование", "Розничная цена"]
].rename(columns={"Розничная цена": "Цена_старая"})

# детали коллизий: все строки с этими артикулами из обоих файлов
coll_rows = []
for a in sorted(coll):
    for src, df in (("НОВЫЙ", new), ("СТАРЫЙ", old)):
        sub = df[df["Артикул"] == a][["Наименование", "Розничная цена"]]
        for _, r in sub.iterrows():
            coll_rows.append({"Артикул": a, "Файл": src,
                              "Наименование": r["Наименование"], "Цена": r["Розничная цена"]})
coll_df = pd.DataFrame(coll_rows)

with pd.ExcelWriter(OUT, engine="openpyxl") as w:
    diff.to_excel(w, sheet_name="Разница цен", index=False)
    only_new.to_excel(w, sheet_name="Только в новом", index=False)
    only_old.to_excel(w, sheet_name="Только в старом", index=False)
    coll_df.to_excel(w, sheet_name="Коллизии_артикулов", index=False)

print(f"Строк (уникальных артикулов): новый={len(new_c)}, старый={len(old_c)}")
print(f"Совпали по артикулу: {len(m)}")
print(f"РАЗНЫЕ ЦЕНЫ: {len(diff)}")
print(f"Только в новом: {len(only_new)} | Только в старом: {len(only_old)}")
print("Сохранено:", OUT)
