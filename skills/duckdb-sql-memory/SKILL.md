# DuckDB + SQL + Память (DashBord / 1C)

Используй этот skill при ЛЮБОМ SQL-запросе к 1C/DuckDB, при работе с DashBord,
при поиске метаданных 1C, при построении запросов к регистрам бухгалтерии,
контрагентам, документам банка. Это единый справочник, консолидирующий всю
глобальную память по DuckDB/SQL/1C/DashBord.

## 1. ПРАВИЛО ПРИОРИТЕТА ИСТОЧНИКОВ (жёсткое, пользователь требовал 3 раза)

Порядок поиска ответа/данных — строго:

1. **Память проекта** (`C:\Users\MZ3\.qwen\projects\c--ai-projects\memory\`) — сначала читать `MEMORY.md` и связанные файлы.
2. **DuckDB** (`semantic_core.duckdb`, `meta_schema.duckdb`) — формальная модель 1C, метаданные, SQL-шаблоны.
3. **Текстовые словари/отчёты** (`scripts/*.md`, `*.txt`) — только как последний resort.

**При упоминании «DashBord»/«Дашборд» — ВСЕГДА сначала загрузить память из ДВУХ мест:**
- `C:\Users\MZ3\.qwen\memories\` (user, cross-project)
- `C:\Users\MZ3\.qwen\projects\c--ai-projects\memory\` (project)

## 2. Доступ к DuckDB

### 2.1. Файлы баз (хост)
- `C:\AI_PROJECTS\Base_DuckDb\data\` — `semantic_core.duckdb`, `meta_schema.duckdb`, `BP_MAIN_COPY.duckdb`

### 2.2. Docker exec (основной способ)
Контейнер: `duckdb_ai_core` (порт 5002), данные в `/app/data/`.

```bash
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb -c "SELECT * FROM query_templates LIMIT 5;"
docker exec duckdb_ai_core duckdb /app/data/meta_schema.duckdb -c "SELECT * FROM meta_nodes LIMIT 5;"
```

Второй контейнер: `duckdb_ai_mcp` (порт 5001).
SSH: `root@192.168.215.174:2222`, пароль `__REDACTED__`.

### 2.3. Ключевые таблицы

**meta_schema.duckdb:**
- `meta_nodes` — узлы метаданных 1C (справочники, документы, регистры)
- `meta_fields` — поля объектов

**semantic_core.duckdb:**
- `graph_nodes_legacy`, `field_registry`, `edge_targets_legacy`, `object_registry`, `relations` — граф модели 1C
- `query_templates` — **18 SQL-шаблонов** (см. раздел 3)
- `query_plans_cache` — **8 готовых планов запросов** (см. раздел 3)

## 3. КЭШ SQL-ЗАПРОСОВ (query_templates / query_plans_cache)

**ПРАВИЛО:** при построении SQL для DashBord — СНАЧАЛА искать готовый шаблон в `query_templates` и `query_plans_cache`. Если нет — построить запрос, проверить, и INSERT нового шаблона в `query_templates`.

### 3.1. query_templates (18 шаблонов)

| Имя | Назначение |
|---|---|
| `DATE_CORRECTION` | Сдвиг дат +2000 лет (shift_date/unshift_date) |
| `REFERENCE` | Запрос к справочнику `_Reference<dec_id>` |
| `TABULAR_SECTION` | Запрос к табличной части `_VT<dec_id>` |
| `REGISTER_COUNTERPARTY` | Регистр бухгалтерии + контрагент (субконто) |
| `REGISTER_ORGANIZATION` | Регистр бухгалтерии + организация |
| `DOC_INCOMING_PAYMENT` | Документ поступления на р/счёт |
| `DOC_OUTGOING_PAYMENT` | Документ списания с р/счёта |
| `DOC_BANK_JOIN_ORG_KONTR_BNK` | Банк: JOIN организация+контрагент+банк |
| `DOCUMENT_COUNTERPARTY` | Документ + контрагент |
| `VT_TABULAR_JOIN` | JOIN табличной части |
| `VT_ADDITIONAL_ATTRS` | VT3058 — дополнительные атрибуты контрагента |
| `VT_PHONES_ADDRESSES` | VT3042 — телефоны/адреса контрагента |
| `NOMENCLATURE_LOOKUP_VIA_TYPE` | Номенклатура через тип |
| `COUNTERPARTY_GROUP_LOOKUP` | Группа контрагента |
| `INVOICE_WITH_ITEMS` | Счёт с табличной частью |
| `ACCOUNT_LOOKUP` | Поиск счёта в плане счетов |
| `BALANCE_TURNOVER` | Сальдо/обороты из регистра |
| `DOC_AGGREGATION_BY_COUNTERPARTY` | Агрегация документов по контрагентам |

### 3.2. query_plans_cache (8 планов)

| Имя | Назначение |
|---|---|
| `accrg1112_dt51_ct62_counterparty` | _AccRg1112, Дт51 Кт62, контрагент |
| `account51_balance_turnover` | Счёт 51: сальдо/обороты |
| `document_counterparty_expense` | Документ расхода + контрагент |
| `doc_receipts_incoming` | Поступления (входящие) |
| `doc_expenses_outgoing` | Расходы (исходящие) |
| `doc_invoices_with_items` | Счета с позициями |
| `counterparties_full_list` | Полный список контрагентов |
| `doc_aggregation_pattern` | Паттерн агрегации документов |

### 3.3. Команды поиска/добавления

```bash
# Найти шаблон
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb \
  -c "SELECT name, sql_text FROM query_templates WHERE name ILIKE '%COUNTERPARTY%';"

# Найти план
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb \
  -c "SELECT name, plan FROM query_plans_cache WHERE name ILIKE '%51%';"

# Добавить новый шаблон (после проверки запроса!)
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb \
  -c "INSERT INTO query_templates (name, description, sql_text) VALUES ('NEW_TEMPLATE', 'описание', 'SELECT ...');"
```

## 4. РЕГИСТР БУХГАЛТЕРИИ _AccRg1112

### 4.1. Ключевые колонки
- `_Fld1116` — сумма (НЕ `_Fld1117`!)
- `_ValueCt1_RRRef` — контрагент через субконто (→ `_Reference119`)
- `_Active` — фильтр: `_Active = 1`
- `_Date_Time` — дата (со сдвигом +2000)

### 4.2. Документ vs Регистр

| Параметр | Документ | Регистр |
|---|---|---|
| Фильтр | `_Posted=1 AND _Marked=0` | `_Active=1` |
| Контрагент | Прямое поле `_FldXXXX_RRRef` | Субконто `_ValueCt1_RRRef` |
| Сумма | Прямое поле | `_Fld1116` |

### 4.3. Сальдо/обороты (CASE-WHEN)
```sql
SELECT
  SUM(CASE WHEN _Fld1116 > 0 THEN _Fld1116 ELSE 0 END) AS debet,
  SUM(CASE WHEN _Fld1116 < 0 THEN -_Fld1116 ELSE 0 END) AS kredit
FROM _AccRg1112
WHERE _Active = 1
  AND _Date_Time >= %s AND _Date_Time < %s
```

**Формула клиента:** `сальдо_конец = сальдо_нач + дебет − кредит`
**Проверка сходимости:** сальдо_нач + обороты = сальдо_конец (иначе ошибка).

### 4.4. Частые ошибки
1. Фильтр по `_Code` в WHERE — **НЕЛЬЗЯ** (использовать `_IDRRef`/`_IDRef`)
2. Сумма из `_Fld1117` вместо `_Fld1116`
3. Контрагент как прямое поле (в регистре — только через субконто)
4. Забытый сдвиг дат +2000
5. `_Marked=0` в регистре (нет такой колонки — только `_Active=1`)

## 5. КОНТРАГЕНТЫ (_Reference119)

- **dec_id = 119**, таблица `_Reference119` (924 записи, 47 колонок)
- Основные поля: `_Fld119`–`_Fld127` (наименование, ИНН, КПП и т.д.)
- `_Description` — наименование (для JOIN)
- `_IDRRef` — ключ для JOIN из документов/регистров

### 5.1. Табличные части
- **VT3042** — телефоны/адреса
- **VT3058** — дополнительные атрибуты

```sql
-- Контрагент + телефоны
SELECT k._Description, t._Fld3042
FROM _Reference119 k
LEFT JOIN _VT3042 t ON k._IDRef = t._IDRef
WHERE k._Description LIKE '%ООО%';
```

## 6. СОСТАВНЫЕ ССЫЛКИ (_TYPE / _RTRef / _RRRef)

В 1C составные ссылки хранятся в 3 колонках:

| Колонка | Назначение |
|---|---|
| `_TYPE` | Код типа (см. таблицу ниже) |
| `_RTRef` | Тип ссылки (для ref-типа) |
| `_RRRef` | Реальная ссылка (для ref-типа) |

### 6.1. Коды _TYPE
| Код | Тип | Колонки |
|---|---|---|
| `0x00` | NULL | — |
| `0x02` | Булево | `_L` |
| `0x03` | Число | `_N` |
| `0x04` | Дата | `_T` |
| `0x05` | Строка | `_S` |
| `0x06` | BLOB | `_B` |
| `0x08` | Ссылка | `_RTRef` + `_RRRef` |

**ПРАВИЛО:** для JOIN по контрагенту/справочнику использовать `_RRRef` (не `_RTRef`!).

## 7. ДАТЫ: СДВИГ +2000 ЛЕТ

1C хранит даты в MSSQL со сдвигом +2000 лет.

```python
from core.dates import shift_date, unshift_date

# При отправке в MSSQL:
db_date = shift_date(python_date)  # +2000 лет

# При получении из MSSQL:
py_date = unshift_date(db_date)   # −2000 лет
```

В SQL:
```sql
-- Сдвиг в запросе
WHERE _Date_Time >= DATEADD(year, 2000, %s)
-- Или в Python: shift_date() перед параметром
```

## 8. АРХИТЕКТУРА DASHBORD

### 8.1. Точка входа
**`dashboard.py`** (НЕ `server.py`!) — `C:\AI_PROJECTS\Qwen_CLI\src\DashBord\site\dashboard.py`

### 8.2. Структура
```
site/
├── dashboard.py      # Точка входа (port 8080)
├── config.py         # DB_CONFIG (pymssql)
├── core/
│   └── dates.py      # shift_date/unshift_date
├── web/              # Веб-слой
└── pages/            # Страницы
    ├── structure/    # 6-я: «Структура» (топ-20 контрагентов)
    ├── account51/    # 4-я: «Счёт 51» (регистр _AccRg1112)
    └── ...           # Другие страницы
```

### 8.3. Страницы (актуально 2026-10-26)
1. Главная
2. Контрагенты
3. Банк (поступления/расходы)
4. **Счёт 51** — дебет/кредит из `_AccRg1112`
5. Номенклатура
6. **Структура** — топ-20 контрагентов по поступлениям/расходам с процентами

### 8.4. Конвенция страниц банка
Обязательные колонки: **Организация, Контрагент, Сумма** + последняя дата + количество.
Фильтр: `_Posted=1` (обязательно).

## 9. ШАБЛОН СТРАНИЦЫ DASHBORD

Каждая страница — папка в `pages/`:
```
pages/<name>/
├── __init__.py    # PAGE = {route, name, html, api_route, query_module}
├── query.py       # SQL-запросы (pymssql, %s параметры)
└── template.html  # HTML-шаблон
```

### 9.1. Пример: structure/query.py
```python
from config import DB_CONFIG
from core.dates import shift_date

def query_structure(date_from, date_to, sort='date', org=None):
    db_from = shift_date(date_from)
    db_to = shift_date(date_to)
    # Поступления: _Document478, kontr=_Fld13954_RRRef, amount=_Fld13957
    # Расходы: _Document512, kontr=_Fld15680_RRRef, amount=_Fld15682
    # JOIN: _Reference119 ON d.{kontr_field} = k._IDRRef
    # Фильтр: _Posted=1 AND _Marked=0
    # Топ-20 + «прочие» с процентами
    return {'income': {...}, 'expenses': {...}}
```

## 10. ЧЕКЛИСТ ПЕРЕД SQL-ЗАПРОСОМ

1. Прочитать `MEMORY.md` (project + user)
2. Поискать шаблон в `query_templates` / `query_plans_cache`
3. Определить: документ или регистр? (фильтры разные!)
4. Контрагент: прямое поле (документ) или субконто (регистр)?
5. Сумма: какое поле? (`_Fld1116` для регистра!)
6. Даты: применить `shift_date()`
7. Составные ссылки: JOIN по `_RRRef`
8. После проверки — INSERT нового шаблона в `query_templates`

## 11. ССЫЛКИ НА ПАМЯТЬ

- `project/structure-page.md` — 6-я страница «Структура»
- `project/account51-page.md` — 4-я страница «Счёт 51»
- `duckdb_query_cache.md` — query_templates/query_plans_cache
- `accounting_registers.md` — регистры бухгалтерии
- `accrg1112_counterparty.md` — контрагент в _AccRg1112
- `accounting_register_logic.md` — сальдо/обороты
- `docker_duckdb_access.md` — docker exec
- `composite_refs.md` — составные ссылки
- `counterparties_query.md` — контрагенты
- `dashbord_architecture.md` — архитектура
- `feedback/bank-pages-convention.md` — конвенция банка
- `feedback/dashbord_sql_query_rule.md` — правило SQL-запросов
- `feedback/dashbord_entry_point.md` — dashboard.py
- `feedback/dashbord_double_memory_load.md` — память из двух мест
- `feedback/check_memory_first.md` — приоритет памяти
