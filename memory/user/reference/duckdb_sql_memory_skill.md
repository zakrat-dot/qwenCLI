---
name: DuckDB+SQL+память — скилл duckdb-sql-memory
description: Единый справочник-скилл по DuckDB/SQL/памяти для DashBord — где лежит, что содержит, когда использовать
type: reference
---

# Скилл: duckdb-sql-memory

**Файл:** `C:\Users\MZ3\.qwen\skills\duckdb-sql-memory\SKILL.md`

Единый справочник, консолидирующий ВСЮ глобальную память по DuckDB/SQL/1C/DashBord:

1. Правило приоритета источников (память → DuckDB → текстовые словари)
2. Доступ к DuckDB (docker exec `duckdb_ai_core`, `/app/data/`, хост `C:\AI_PROJECTS\Base_DuckDb\data\`)
3. Кэш SQL-запросов: `query_templates` (18) + `query_plans_cache` (8) — команды поиска/INSERT
4. Регистр бухгалтерии `_AccRg1112` (колонки, субконто, сальдо/обороты, частые ошибки)
5. Контрагенты `_Reference119` + VT3042/VT3058
6. Составные ссылки `_TYPE`/`_RTRef`/`_RRRef` (коды типов)
7. Сдвиг дат +2000 лет (shift_date/unshift_date)
8. Архитектура DashBord (dashboard.py, core/web/pages, 6 страниц)
9. Конвенция страниц банка
10. Чеклист перед SQL-запросом

**Когда использовать:** при любом SQL-запросе к 1C/DuckDB, при работе с DashBord, при поиске метаданных 1C.

**Как применять:** читать файл целиком как справочник; при SQL — сначала раздел 3 (кэш запросов), затем раздел 10 (чеклист).
