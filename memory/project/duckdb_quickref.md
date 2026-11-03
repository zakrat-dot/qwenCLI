---
name: DuckDB базы semantic_core и meta_schema — быстрый справочник
description: Как искать и сопоставлять данные в DuckDB базах проекта Base_DuckDb: meta_schema.duckdb и semantic_core.duckdb
type: project
---

## Где лежат

```
C:\AI_PROJECTS\Base_DuckDb\data\
  meta_schema.duckdb    — структура 1C объектов (узлы + поля)
  semantic_core.duckdb  — семантический слой (концепты, синонимы, гипотезы)
  BP_MAIN_COPY.duckdb   — копия данных из MSSQL
```

## meta_schema.duckdb — структура 1C

**Скрипт построения:** `src/build_meta_schema.py`

### Таблицы

| Таблица | Что хранит |
|---------|-----------|
| `nodes` | Все объекты 1C (справочники, документы, регистры). `dec_id` = числовой ID, `hex_id` = GUID, `object_name` = имя, `class` = тип (Catalog, Document...), `synonym` = синоним на русском |
| `fields` | Все поля объектов. `node_id` → `nodes.dec_id`, `field_sql_name` = имя колонки в MSSQL, `field_name` = имя поля в 1C, `target_dec_id` = ссылка на другой объект (ссылочные поля) |
| `suffixes` | Суффиксы таблиц (VT, DT и т.д.) |

### Как найти физическую таблицу

```sql
-- 1. Найти объект по имени/синониму
SELECT dec_id, object_name, synonym, class, hex_id
FROM nodes WHERE synonym LIKE '%Контрагент%' OR object_name LIKE '%Контрагент%';

-- 2. Получить все поля объекта
SELECT field_sql_name, field_name, business_name, target_dec_id, storage_type
FROM fields WHERE node_id = <dec_id>;

-- 3. Физическая таблица в MSSQL = '_' + class + dec_id
-- Например: Catalog + 119 → _Reference119
```

### Как найти табличные части

```sql
-- VT (tabular sections) привязаны к родительскому узлу
SELECT f.field_sql_name, f.field_name, f.business_name
FROM fields f
WHERE f.vt_parent_id = <dec_id>;

-- Каждая VT = отдельная таблица: _Reference<dec_id>_VT<vt_dec_id>
```

## semantic_core.duckdb — семантический слой

**Скрипт построения:** `src/build_semantic_core.py`

### Таблицы

| Таблица | Что хранит |
|---------|-----------|
| `source_meta_nodes` | Копия `nodes` из meta_schema (для каждой БД отдельно) |
| `source_meta_fields` | Копия `fields` из meta_schema |
| `concepts` | Бизнес-концепты (счета, контрагенты, номенклатура) |
| `synonyms` | Синонимы концептов |
| `relations` | Связи между концептами |
| `hypotheses` | Гипотезы о данных |
| `business_models` | Бизнес-модели |

### Как найти таблицу через семантику

```sql
-- 1. Найти концепт по ключевому слову
SELECT * FROM concepts WHERE name LIKE '%контрагент%';

-- 2. Найти связанные физические объекты
SELECT smn.* FROM source_meta_nodes smn
JOIN relations r ON smn.dec_id = r.target_dec_id
WHERE r.concept_id = <concept_id>;
```

## Практический алгоритм поиска

1. **Знаю бизнес-термин** → ищу в `meta_schema.nodes.synonym` или `semantic_core.concepts`
2. **Нашел dec_id** → физическая таблица MSSQL = `_Reference<dec_id>` (для Catalog) или `_Document<dec_id>` (для Document)
3. **Нужны поля** → `meta_schema.fields WHERE node_id = dec_id`
4. **Нужны табличные части** → `meta_schema.fields WHERE vt_parent_id = dec_id`
5. **Нужны связи** → `fields.target_dec_id` показывает на какой объект ссылается поле

## Пример: Контрагенты

```
synonym = 'Контрагенты' → dec_id = 119, class = Catalog
Физическая таблица: _Reference119
Табличные части: _Reference119_VT3042 (телефоны), _Reference119_VT3058 (доп. реквизиты)
```

## Why

Пользователь просил сохранить короткий справочник по DuckDB базам, чтобы не повторять исследование при будущих задачах.

## How to apply

При любом запросе на поиск данных в 1C базе — сначала смотреть в meta_schema, потом строить SQL запрос к MSSQL.
