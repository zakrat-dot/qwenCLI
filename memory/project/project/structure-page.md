---
name: structure-page
description: 6-я страница DashBord «Структура» — топ-20 контрагентов по поступлениям/расходам с процентами; _Document478/_Document512
type: project
---

# Страница «Структура» (6-я страница DashBord)

Добавлена 2026-10-26. Файлы: `C:\AI_PROJECTS\Qwen_CLI\src\DashBord\site\pages\structure\` (`__init__.py`, `query.py`, `template.html`).

## Что сделано

- **Route:** `/structure`, **API:** `/api/structure`, **модуль:** `pages.structure.query`
- **Название:** «Структура» — структура поступлений и расходов по контрагентам
- **Входные параметры:** `date_from`, `date_to`, `sort` (date/sum), `org` (не используется в SQL, зарезервировано)
- **Возврат:** `{'income': {total, slices}, 'expenses': {total, slices}}` — slices = список `{kontr, total, percent}`

## Логика запроса

**Топ-20 контрагентов + «прочие»:**
- `query_structure(date_from, date_to, sort, org)` → вызывает `_query_by_counterparty()` для поступлений и расходов
- `_query_by_counterparty(cur, doc_table, kontr_field, amount_field, db_from, db_to)`:
  ```sql
  SELECT k._Description AS kontr, SUM(d.{amount_field}) AS total
  FROM {doc_table} d
  LEFT JOIN _Reference119 k ON d.{kontr_field} = k._IDRRef
  WHERE d._Posted = 1 AND d._Marked = 0
    AND d._Date_Time >= %s AND d._Date_Time < DATEADD(day, 1, %s)
  GROUP BY k._Description ORDER BY total DESC
  ```
- `_top20_with_others(rows)`: берёт топ-20, остаток сворачивает в строку «прочие», считает процент от общего итога

## Таблицы и поля (1C физ. хранение)

| Параметр | Поступления | Расходы |
|---|---|---|
| Документ | `_Document478` (ПоступлениеНаРасчетныйСчет) | `_Document512` (СписаниеСРасчетногоСчета) |
| Контрагент | `_Fld13954_RRRef` → `_Reference119` | `_Fld15680_RRRef` → `_Reference119` |
| Сумма | `_Fld13957` | `_Fld15682` |
| Фильтр | `_Posted=1 AND _Marked=0` | `_Posted=1 AND _Marked=0` |

**Важно:**
- Контрагент — составная ссылка `_RRRef` (не `_RTRef`!) — JOIN по `_IDRRef` справочника
- Сумма — прямое поле документа (не табличная часть)
- Даты: `shift_date` из `core.dates` (+2000 лет), `DB_CONFIG` из `config`
- `LEFT JOIN` — контрагент может быть пустым (NULL → «прочие»)

## Why
Страница показывает, кто основные контрагенты по поступлениям/расходам за период — топ-20 + «прочие» с процентами.

## How to apply
- При доработке страницы — читать `pages/structure/query.py`
- Новые страницы банка — по конвенции `feedback/bank-pages-convention.md` (Организация/Контрагент/Сумма + фильтр `_Posted=1`)
- SQL-шаблоны — сначала искать в `query_templates`/`query_plans_cache` (DuckDB semantic_core)
