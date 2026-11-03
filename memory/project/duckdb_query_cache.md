---
name: DuckDB semantic_core — таблицы query_templates и query_plans_cache
description: В базе semantic_core.duckdb хранятся 18 SQL шаблонов запросов к MSSQL (регистрам, документам, справочникам) и 8 планов запросов из всех страниц DashBord. Доступ через docker exec
type: project
---

## Таблицы памяти SQL-запросов в semantic_core.duckdb

В базе `semantic_core.duckdb` (контейнер `duckdb_ai_core`, путь `/app/data/`) хранятся две таблицы для кеширования и повторного использования паттернов запросов к MSSQL 1С:

### query_templates — шаблоны SQL-запросов
**Структура:** relation_type, sql_template, description  
**Записей:** 18 (3 базовых + 15 из кода DashBord)

| Категория | Шаблоны | Описание |
|-----------|---------|----------|
| Базовые паттерны | DATE_CORRECTION, REFERENCE, TABULAR_SECTION | Сдвиг дат -2000 лет, JOIN справочников, ТЧ |
| Регистр Хозрасчетный | REGISTER_COUNTERPARTY (_ValueCt1_RRRef → _Reference119), REGISTER_ORGANIZATION (_Fld1113RRef → _Reference150) | Контрагент через субконто Ct1, организация прямым полем |
| Документы поступления/расходы | DOC_INCOMING_PAYMENT (_Document478), DOC_OUTGOING_PAYMENT (_Document512) | Прямые поля контрагента в документах |
| JOIN-паттерны | DOC_BANK_JOIN_ORG_KONTR_BNK, DOCUMENT_COUNTERPARTY | Организация + Контрагент + Банк через прямые поля |
| Табличные части VT | VT_TABULAR_JOIN, VT_ADDITIONAL_ATTRS (VT3058), VT_PHONES_ADDRESSES (VT3042) | JOIN по родительскому IDRRef, типы значений 0x03=число, 0x00=строка, 0x01=дата |
| Справочники и агрегация | NOMENCLATURE_LOOKUP_VIA_TYPE (_Reference137), COUNTERPARTY_GROUP_LOOKUP (self-join по _ParentIDRRef), INVOICE_WITH_ITEMS (_Document518X1 + VT товаров) | Номенклатура, группы контрагентов с кэшем, счета на оплату |
| Универсальные шаблоны | ACCOUNT_LOOKUP (_Acc36), BALANCE_TURNOVER (CASE по датам для Дт/Кт), DOC_AGGREGATION_BY_COUNTERPARTY | Поиск IDRRef счетов, обороты/сальдо, агрегация сводок |

### query_plans_cache — планы запросов
**Структура:** plan_hash, metadata_hash, plan_json  
**Записей:** 8 (по одному на каждую страницу дашборда + универсальный шаблон)

| plan_hash | Страница | Источник данных | Ключевые поля контрагента/организации |
|-----------|---------|-----------------|--------------------------------------|
| accrg1112_dt51_ct62_counterparty | payment_receipts | _AccRg1112 (регистр) | субконто Ct1 → _Reference119, прямое поле org → _Reference150 |
| account51_balance_turnover | account51 | _AccRg1112 + CASE по датам | Дт/Кт сальдо и обороты через CASE WHEN |
| document_counterparty_expense | expenses | _Document512 | прямое поле контрагента, организация, банк |
| doc_receipts_incoming | receipts | _Document478 | _Fld13954_RRRef → kontr, _Fld13947RRef → org, _Fld13949RRef → bank |
| doc_expenses_outgoing | expenses | _Document512 | _Fld15680_RRRef → kontr, _Fld15674RRef → org, _Fld15675RRef → bank |
| doc_invoices_with_items | invoices | _Document518X1 + VT товаров/услуг | отдельный lookup контрагента и организации по ссылкам из документа |
| counterparties_full_list | counterparties | _Reference119 + группы, телефоны (VT3042), доп. реквизиты (VT3058) | self-join для групп с кэшем parent_id |
| doc_aggregation_pattern | receipts+expenses | Универсальный шаблон агрегации по контрагенту из таблицы документа | GROUP BY k._Description, ORDER BY total DESC |

### Как использовать при разработке новых страниц дашборда

1. **Сначала проверить query_templates** — есть ли готовый паттерн JOIN для нужного типа данных (регистр vs документ)
2. **Проверить query_plans_cache** — есть ли похожий план запроса, который можно адаптировать под новую страницу  
3. **Фильтры:** регистр → `_Active=1`, документы → `_Posted=1 AND _Marked=0`
4. **Даты в MSSQL 1С хранятся со сдвигом +2000 лет** — использовать DATE_CORRECTION шаблон

### Запрос к таблицам через docker exec

```bash
# Все шаблоны
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb -c "SELECT relation_type, description FROM query_templates;"

# Поиск по ключевому слову в описании или SQL шаблоне  
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb -c "SELECT * FROM query_templates WHERE sql_template LIKE '%_Reference119%';"

# Все планы запросов
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb -c "SELECT plan_hash, SUBSTR(plan_json, 1, 60) AS preview FROM query_plans_cache;"
```

**Why:** При создании новых страниц дашборда или отладке запросов к MSSQL можно быстро найти рабочий паттерн JOIN без повторного исследования структуры таблиц. Шаблоны содержат реальные поля из кода DashBord (payment_receipts, account51, expenses, receipts, counterparties, invoices).
**How to apply:** Перед написанием нового SQL-запроса к MSSQL 1С сначала проверяй query_templates и query_plans_cache в semantic_core.duckdb через docker exec.
