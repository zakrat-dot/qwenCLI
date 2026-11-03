---
name: Формальная модель 1C в DuckDB — структура и связи
description: Полная формальная модель структуры 1C в meta_schema.duckdb и semantic_core.duckdb: DEC_ID/HEX_ID, parent_dec_id vs target_dec_id, ссылочные поля, табличные части
type: project
---

## Где лежат

```
C:\AI_PROJECTS\Base_DuckDb\data\
  meta_schema.duckdb    — физическое описание структуры 1C
  semantic_core.duckdb  — нормализованное описание + семантика
  BP_MAIN_COPY.duckdb   — копия данных из MSSQL
```

## Ключевые инварианты

### 1. DEC_ID и HEX_ID
```
HEX_ID = HEX(DEC_ID)  — это один и тот же идентификатор
```
Ключевой идентификатор — `dec_id`. HEX — только другое представление.

### 2. parent_dec_id vs target_dec_id — НЕ взаимозаменяемы!
```
parent_dec_id  → к какому основному объекту относится узел (для табличных частей)
target_dec_id  → на какой объект ссылается конкретное поле (ссылочные поля)
```

### 3. Табличные части
```
parent_dec_id IS NULL   → основной объект
parent_dec_id IS NOT NULL → табличная часть, значение = dec_id родителя
```

### 4. Ссылочные поля
```
_TYPE = 0x08  → ссылочный тип (Ref)
_RTRef        → содержит HEX_ID конкретного объекта-цели
_RRRef        → для составных типов
```
Важно: `_TYPE` описывает **тип значения**, `_RTRef` описывает **конкретный объект**.

### 5. Составные типы
```
<Имя>_TYPE + <Имя>_RTRef + <Имя>_RRRef = один логический реквизит
```

## Таблицы meta_schema.duckdb

| Таблица | Что хранит |
|---------|-----------|
| `nodes` | Все объекты 1C. `dec_id`, `hex_id`, `object_name`, `class`, `synonym`, `parent_dec_id` |
| `fields` | Все поля. `node_id` → `nodes.dec_id`, `field_sql_name`, `field_name`, `target_dec_id`, `vt_parent_id` |
| `suffixes` | Суффиксы таблиц (VT, DT) |

## Таблицы semantic_core.duckdb

| Таблица | Что хранит |
|---------|-----------|
| `source_meta_nodes` | Копия nodes (для каждой БД отдельно, с `database_name`) |
| `source_meta_fields` | Копия fields (с `database_name`) |
| `concepts` | Бизнес-концепты |
| `synonyms` | Синонимы концептов |
| `relations` | Связи между концептами |
| `hypotheses` | Гипотезы о данных |
| `business_models` | Бизнес-модели |

## Алгоритм поиска физической таблицы

```sql
-- 1. Найти объект по синониму/имени
SELECT dec_id, object_name, synonym, class, hex_id
FROM nodes
WHERE synonym LIKE '%Контрагент%' OR object_name LIKE '%Контрагент%';

-- 2. Получить все поля объекта
SELECT field_sql_name, field_name, business_name, target_dec_id, storage_type
FROM fields
WHERE node_id = <dec_id>;

-- 3. Физическая таблица в MSSQL:
--    Catalog → _Reference<dec_id>
--    Document → _Document<dec_id>
--    AccountingRegister → _AccRg<dec_id>
--    ChartOfAccounts → _Acc<dec_id>

-- 4. Найти табличные части объекта
SELECT n.dec_id, n.object_name, n.synonym
FROM nodes n
WHERE n.parent_dec_id = <dec_id>;
-- Физическая таблица: _Reference<dec_id>_VT<vt_dec_id>
```

## Формальная цепочка идентификации

```
HEX_ID → DEC_ID → object
              ↓
     parent_dec_id → родитель (для табличных частей)
              ↓
     target_dec_id → объект-ссылка (для полей)
              ↓
     _TYPE = 0x08 → Ref
              ↓
     _RTRef → HEX_ID → DEC_ID → конкретный объект
```

## Почему это важно

- Без понимания `parent_dec_id` vs `target_dec_id` невозможно правильно сопоставить табличные части с родителями
- Без понимания `_TYPE` vs `_RTRef` невозможно определить, на какой объект ссылается поле
- HEX и DEC — это один идентификатор, не два разных
- Справочник `структраБУХ.html` более полный, чем DuckDB — использовать как основной источник при написании запросов

## Справочники метаданных

```
C:\AI_PROJECTS\Base_DuckDb\src\структраБУХ.html   — полный словарь метаданных
C:\AI_PROJECTS\Base_DuckDb\src\СтруктураБУХ.txt   — текстовая версия
C:\AI_PROJECTS\Base_DuckDb\src\db_schema.json     — JSON структура
```
