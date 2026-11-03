# -*- coding: utf-8 -*-
"""Универсальное сравнение двух Excel-файлов по ключу (артикул, код и т.п.).

Сравнивает значения (цены, остатки, строки) между двумя файлами:
  - «Различия»         — ключи, где значение отличается
  - «Только в 1»       — ключи, которых нет во втором файле
  - «Только в 2»       — ключи, которых нет в первом файле
  - «Коллизии»         — ключи, занятые разными товарами (2+ наименования)
  - «Fuzzy_совпадения» — (опционально, --fuzzy) похожие наименования
                         для ключей, не совпавших точно

Автоопределение:
  - строка заголовка: первая из 15, где встречается колонка-ключ
  - колонка значения: имя содержит «цена», иначе последняя числовая

Пример:
  py compare_excel.py новый.xlsx старый.xlsx --key Артикул --fuzzy
"""
import argparse
import os
import sys

import pandas as pd

TOL_DEFAULT = 0.001


def norm_key(x):
    """Ключ в строку: 12345.0 -> '12345', пробелы убираем."""
    if pd.isna(x):
        return ""
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x).strip()


def find_header_row(path, key_name):
    """Первая строка из 15, где есть колонка с именем ключа."""
    raw = pd.read_excel(path, header=None, nrows=15)
    for i in range(len(raw)):
        vals = [str(v).strip().lower() for v in raw.iloc[i].tolist() if pd.notna(v)]
        if key_name.lower() in vals:
            return i
    counts = raw.apply(lambda r: int(r.notna().sum()), axis=1)
    return int(counts.idxmax())


def detect_value_col(df, exclude):
    """Колонка значения: имя содержит «цена», иначе последняя числовая."""
    for c in df.columns:
        if c in exclude:
            continue
        if "цена" in str(c).lower():
            return c
    num = [c for c in df.columns
           if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]
    return num[-1] if num else None


def load(path, key_col, name_col):
    header = find_header_row(path, key_col)
    df = pd.read_excel(path, header=header)
    df.columns = [str(c).strip() for c in df.columns]
    if key_col not in df.columns:
        sys.exit(f"ОШИБКА: колонка '{key_col}' не найдена в {path}\n"
                 f"Колонки: {df.columns.tolist()}")
    df = df.rename(columns={key_col: "Ключ"})
    if name_col and name_col in df.columns:
        df = df.rename(columns={name_col: "Наименование"})
    else:
        df["Наименование"] = ""
    df["Ключ"] = df["Ключ"].map(norm_key)
    df = df[df["Ключ"] != ""]
    return df


def colliding_keys(df):
    """Ключи, у которых в файле 2+ разных наименования (разные товары)."""
    g = df.groupby("Ключ")["Наименование"].nunique()
    return set(g[g > 1].index)


def fuzzy_match(only_df, other_df, threshold, val_col, direction):
    """Для ключей из only_df ищет похожие наименования в other_df."""
    from rapidfuzz import fuzz, process
    name_to_key = {}
    for k, n in zip(other_df["Ключ"], other_df["Наименование"].astype(str)):
        name_to_key.setdefault(n, k)
    choices = list(name_to_key.keys())
    if not choices:
        return pd.DataFrame()
    val_by_key = dict(zip(other_df["Ключ"], other_df["Значение"]))
    rows = []
    for _, r in only_df.iterrows():
        q = str(r["Наименование"]).strip()
        if not q:
            continue
        hit = process.extractOne(q, choices, scorer=fuzz.token_set_ratio)
        if hit and hit[1] >= threshold:
            k2 = name_to_key[hit[0]]
            rows.append({
                "Направление": direction,
                "Ключ_1": r["Ключ"],
                "Наименование_1": r["Наименование"],
                "Значение_1": r[val_col],
                "Ключ_2": k2,
                "Наименование_2": hit[0],
                "Значение_2": val_by_key.get(k2, ""),
                "Score": int(hit[1]),
            })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description="Сравнение двух Excel-файлов по ключу")
    ap.add_argument("file1", help="Первый файл (обычно новый)")
    ap.add_argument("file2", help="Второй файл (обычно старый)")
    ap.add_argument("--key", default="Артикул",
                    help="Колонка-ключ в файле 1 (по умолчанию Артикул)")
    ap.add_argument("--key2", default=None,
                    help="Колонка-ключ в файле 2 (по умолчанию = --key)")
    ap.add_argument("--name", default="Наименование",
                    help="Колонка наименования (по умолчанию Наименование)")
    ap.add_argument("--value", default=None,
                    help="Колонка значения (цена/остаток). Авто: колонка с «цена»")
    ap.add_argument("--tol", type=float, default=TOL_DEFAULT,
                    help="Допуск для числового сравнения (по умолчанию 0.001)")
    ap.add_argument("--out", default=None,
                    help="Путь к результату (авто: рядом с файлом 1)")
    ap.add_argument("--fuzzy", action="store_true",
                    help="Fuzzy-совпадения наименований для несовпавших ключей")
    ap.add_argument("--fuzzy-threshold", type=int, default=80,
                    help="Порог fuzzy-похожести 0-100 (по умолчанию 80)")
    args = ap.parse_args()

    key2 = args.key2 or args.key

    df1 = load(args.file1, args.key, args.name)
    df2 = load(args.file2, key2, args.name)

    # --- колонка значения ---
    if args.value:
        if args.value not in df1.columns or args.value not in df2.columns:
            sys.exit(f"ОШИБКА: колонка значения '{args.value}' не найдена.\n"
                     f"Файл1: {df1.columns.tolist()}\nФайл2: {df2.columns.tolist()}")
        val1 = val2 = args.value
    else:
        val1 = detect_value_col(df1, exclude={"Ключ", "Наименование"})
        val2 = detect_value_col(df2, exclude={"Ключ", "Наименование"})
        if not val1 or not val2:
            sys.exit("ОШИБКА: не удалось найти колонку значения. Укажите --value")
    df1 = df1.rename(columns={val1: "Значение"})
    df2 = df2.rename(columns={val2: "Значение"})
    print(f"Колонка значения: файл1='{val1}', файл2='{val2}'")

    # --- коллизии: один ключ -> разные товары ---
    coll = colliding_keys(df1) | colliding_keys(df2)
    print(f"Коллизии ключей (разные товары под одним ключом): "
          f"{sorted(coll) if coll else 'нет'}")

    d1 = df1[~df1["Ключ"].isin(coll)].drop_duplicates(subset="Ключ", keep="first")
    d2 = df2[~df2["Ключ"].isin(coll)].drop_duplicates(subset="Ключ", keep="first")

    # --- точное сравнение по ключу ---
    m = d1[["Ключ", "Наименование", "Значение"]].merge(
        d2[["Ключ", "Значение"]].rename(columns={"Значение": "Значение_2"}),
        on="Ключ", how="inner")
    m = m.rename(columns={"Значение": "Значение_1"})

    numeric = (pd.api.types.is_numeric_dtype(m["Значение_1"])
               and pd.api.types.is_numeric_dtype(m["Значение_2"]))
    if numeric:
        m["Разница"] = m["Значение_1"] - m["Значение_2"]
        diff = m[m["Разница"].abs() > args.tol].copy()
        diff = diff.sort_values("Ключ")[
            ["Ключ", "Наименование", "Значение_1", "Значение_2", "Разница"]]
    else:
        diff = m[m["Значение_1"].astype(str) != m["Значение_2"].astype(str)].copy()
        diff = diff.sort_values("Ключ")[
            ["Ключ", "Наименование", "Значение_1", "Значение_2"]]

    only1 = d1[~d1["Ключ"].isin(d2["Ключ"])][
        ["Ключ", "Наименование", "Значение"]].rename(columns={"Значение": "Значение_1"})
    only2 = d2[~d2["Ключ"].isin(d1["Ключ"])][
        ["Ключ", "Наименование", "Значение"]].rename(columns={"Значение": "Значение_2"})

    # --- детали коллизий ---
    coll_rows = []
    for k in sorted(coll):
        for tag, df in (("Файл1", df1), ("Файл2", df2)):
            for _, r in df[df["Ключ"] == k].iterrows():
                coll_rows.append({"Ключ": k, "Файл": tag,
                                  "Наименование": r["Наименование"],
                                  "Значение": r["Значение"]})
    coll_df = pd.DataFrame(coll_rows)

    # --- fuzzy для несовпавших ключей ---
    fuzzy_df = pd.DataFrame()
    if args.fuzzy:
        f1 = fuzzy_match(only1, d2, args.fuzzy_threshold, "Значение_1", "1→2")
        f2 = fuzzy_match(only2, d1, args.fuzzy_threshold, "Значение_2", "2→1")
        parts = [p for p in (f1, f2) if len(p)]
        if parts:
            fuzzy_df = pd.concat(parts, ignore_index=True).sort_values(
                "Score", ascending=False)

    # --- вывод ---
    if not args.out:
        base1 = os.path.splitext(os.path.basename(args.file1))[0]
        base2 = os.path.splitext(os.path.basename(args.file2))[0]
        out_dir = os.path.dirname(os.path.abspath(args.file1))
        args.out = os.path.join(out_dir, f"Сравнение_{base1}_vs_{base2}.xlsx")

    with pd.ExcelWriter(args.out, engine="openpyxl") as w:
        diff.to_excel(w, sheet_name="Различия", index=False)
        only1.to_excel(w, sheet_name="Только в 1", index=False)
        only2.to_excel(w, sheet_name="Только в 2", index=False)
        coll_df.to_excel(w, sheet_name="Коллизии", index=False)
        if len(fuzzy_df):
            fuzzy_df.to_excel(w, sheet_name="Fuzzy_совпадения", index=False)

    print(f"Строк данных: файл1={len(df1)}, файл2={len(df2)} "
          f"(уникальных ключей: {len(d1)}, {len(d2)})")
    print(f"Совпали по ключу: {len(m)}")
    print(f"РАЗЛИЧИЯ: {len(diff)}")
    print(f"Только в файле 1: {len(only1)} | Только в файле 2: {len(only2)}")
    print(f"Коллизии: {len(coll)}")
    if args.fuzzy:
        print(f"Fuzzy-совпадения (порог {args.fuzzy_threshold}): {len(fuzzy_df)}")
    print("Сохранено:", args.out)


if __name__ == "__main__":
    main()
