---
name: При построении SQL-запросов для DashBord — сначала искать шаблоны в DuckDB query_templates и query_plans_cache
description: Жёсткое правило: перед написанием нового SQL-запроса к MSSQL 1С для дашборда всегда проверять готовые паттерны JOIN, поля документов/регистра и фильтры в таблицах semantic_core.duckdb через docker exec. Это экономит время и предотвращает ошибки с субконто vs прямыми полями
type: feedback
---

## Правило: SQL-запросы для DashBord — сначала DuckDB шаблоны, потом кодирование

При любой задаче по построению или отладке SQL-запросов к MSSQL базе 1С (BP_MAIN_COPY) для проекта DashBord **всегда** выполнять следующий порядок действий:

### Шаг 0 — Проверить query_templates и query_plans_cache в DuckDB
```bash
# Все шаблоны
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb -c "SELECT relation_type, description FROM query_templates;"

# Поиск по ключевому слову (например контрагент)
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb -c "SELECT * FROM query_templates WHERE sql_template LIKE '%_Reference119%';"

# Все планы запросов — найти похожую страницу дашборда
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb -c "SELECT plan_hash, SUBSTR(plan_json, 1, 80) AS preview FROM query_plans_cache;"
```

### Почему это обязательно?
- В базе semantic_core.duckdb хранятся **реальные рабочие паттерны** из кода DashBord (payment_receipts, account51, expenses, receipts, counterparties, invoices)
- Там зафиксированы критические различия: регистр Хозрасчетный использует субконто Ct1 (`_ValueCt1_RRRef → _Reference119`), а документы — прямые поля (`_FldXXXXX_RRRef`)
- Фильтры уже известны: `_Active=1` для регистра, `_Posted=1 AND _Marked=0` для документов  
- Даты в MSSQL 1С хранятся со сдвигом +2000 лет

### Что делать если шаблон найден?
Адаптировать его под новую задачу — поменять счёт, период, добавить/убрать JOIN. Не писать запрос с нуля.

### Что делать если шаблона нет?
После успешного написания нового запроса **добавить** новый паттерн в query_templates и план в query_plans_cache через docker exec + SQL INSERT. Так база знаний растёт.
