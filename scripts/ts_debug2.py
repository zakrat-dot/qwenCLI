# -*- coding: utf-8 -*-
"""Тест parse_timestamp на реальном тексте с \u202f."""
import re

MONTHS = {
    'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'мая': 5, 'июн': 6,
    'июл': 7, 'авг': 8, 'сент': 9, 'окт': 10, 'нояб': 11, 'дек': 12,
}

def parse_timestamp(ts):
    if not ts:
        return ""
    ts = ts.strip()
    m = re.match(r"(\d{1,2})\s+([а-яё]+)\.?\s+(\d{4})\s*г?\.?,?\s*(\d{1,2}:\d{2}(?::\d{2})?)", ts)
    if m:
        day = int(m.group(1))
        month_abbr = m.group(2).lower()
        year = int(m.group(3))
        time_str = m.group(4)
        month = None
        for abbr, num in MONTHS.items():
            if month_abbr.startswith(abbr):
                month = num
                break
        if month:
            return f"{year:04d}-{month:02d}-{day:02d} {time_str}"
    return ts

# Реальный текст из debug
ts_real = '26 окт. 2026\u202fг., 21:51:09 MSK'
print("Вход:  " + repr(ts_real))
print("Результат: " + repr(parse_timestamp(ts_real)))

# Проверим regex по частям
steps = [
    (r"\d{1,2}", "день"),
    (r"\d{1,2}\s+", "день+пробел"),
    (r"\d{1,2}\s+[а-яё]+", "день+месяц"),
    (r"\d{1,2}\s+[а-яё]+\.?", "день+месяц+точка"),
    (r"\d{1,2}\s+[а-яё]+\.?\s+", "день+месяц+точка+пробел"),
    (r"\d{1,2}\s+[а-яё]+\.?\s+\d{4}", "день+месяц+год"),
    (r"\d{1,2}\s+[а-яё]+\.?\s+\d{4}\s*", "день+месяц+год+пробел"),
    (r"\d{1,2}\s+[а-яё]+\.?\s+\d{4}\s*г?", "день+месяц+год+г"),
    (r"\d{1,2}\s+[а-яё]+\.?\s+\d{4}\s*г?\.?", "день+месяц+год+г+точка"),
    (r"\d{1,2}\s+[а-яё]+\.?\s+\d{4}\s*г?\.?,?", "день+месяц+год+г+запятая"),
    (r"\d{1,2}\s+[а-яё]+\.?\s+\d{4}\s*г?\.?,?\s*", "день+месяц+год+г+запятая+пробел"),
    (r"(\d{1,2})\s+([а-яё]+)\.?\s+(\d{4})\s*г?\.?,?\s*(\d{1,2}:\d{2}(?::\d{2})?)", "ПОЛНЫЙ"),
]
for pat, label in steps:
    m = re.match(pat, ts_real)
    print(f"  {label:30s} match={bool(m)}")
